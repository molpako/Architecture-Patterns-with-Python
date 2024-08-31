import abc
from datetime import date

from sqlalchemy.ext.asyncio import AsyncConnection

from domain import model
from backend.query import AsyncQuerier


class AbstractProductRepository(abc.ABC):
    def __init__(self):
        self.seen: set[model.Product] = set()

    async def add(self, product: model.Product) -> None:
        self.seen.add(product)

    async def get(self, sku: str) -> model.Product:
        if product := await self._get(sku):
            self.seen.add(product)
        return product

    @abc.abstractmethod
    async def _get(self, sku: str) -> model.Product:
        raise NotImplementedError

    @abc.abstractmethod
    async def update(self, product: model.Product) -> None:
        raise NotImplementedError


class BackendRepository(AbstractProductRepository):
    def __init__(self, conn: AsyncConnection):
        super().__init__()
        self.querier = AsyncQuerier(conn)

    async def add(self, product: model.Product) -> None:
        await super().add(product)
        await self.update(product)

    async def update(self, product: model.Product) -> None:
        await self.querier.create_or_update_product(
            sku=product.sku, version_number=product.version_number
        )
        for b in product.batches:
            batch = await self.querier.create_or_update_batch(
                reference=b.reference,
                sku=b.sku,
                purchased_quantity=b._purchased_quantity,
                eta=b.eta,
            )
            if not batch:
                continue

            await self.querier.clear_order_lines(batch_id=batch.id)
            for o in b._allocations:
                order_line = await self.querier.add_order_line(
                    sku=o.sku, qty=o.qty, orderid=o.orderid
                )
                if not order_line:
                    continue
                await self.querier.add_allocation(
                    orderline_id=order_line.id, batch_id=batch.id
                )

    async def _get(self, sku: str) -> model.Product | None:
        if not (product := await self.querier.get_product(sku=sku)):
            return None

        batches = [
            await self.batch_to_domain(
                b.id, b.reference, b.sku, b.purchased_quantity, b.eta
            )
            async for b in self.querier.get_batch(sku=product.sku)
            if b.reference is not None
        ]

        return model.Product(
            sku=product.sku,
            batches=batches,
            version_number=product.version_number,
        )

    async def batch_to_domain(
        self, id: int, ref: str, sku: str, qty: int, eta: date | None
    ) -> model.Batch:
        batch = model.Batch(ref, sku, qty, eta)
        batch._allocations = {
            model.OrderLine(o.orderid, o.sku, o.qty)
            async for o in self.querier.get_orderlines(id=id)
            if not (o.orderid is None or o.sku is None)
        }
        return batch
