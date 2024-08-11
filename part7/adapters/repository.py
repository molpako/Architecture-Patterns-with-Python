import abc
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncConnection

from domain import model
from backend.query import AsyncQuerier


class AbstractProductRepository(abc.ABC):
    @abc.abstractmethod
    async def add_batch(self, batch: model.Batch) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def add(self, batch: model.Product) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, sku: str) -> model.Product:
        raise NotImplementedError

    @abc.abstractmethod
    async def list(self) -> AsyncIterator[model.Product]:
        if False:
            yield 1


class BackendRepository(AbstractProductRepository):
    def __init__(self, conn: AsyncConnection):
        self.querier = AsyncQuerier(conn)

    async def add_batch(self, batch: model.Batch) -> None:
        await self.querier.add_batch(
            reference=batch.reference,
            sku=batch.sku,
            purchased_quantity=batch._purchased_quantity,
            eta=batch.eta,
        )

    async def add(self, product: model.Product) -> None:
        await self.querier.add_product(
            sku=product.sku, version_number=product.version_number
        )

    async def get(self, sku: str) -> model.Product | None:
        rows = self.querier.get_product(sku=sku)
        first = await anext(rows)
        if first is None:
            return None

        batches: list[model.Batch] = []
        if first.reference is not None and first.purchased_quantity is not None:
            batches.append(
                model.Batch(
                    first.reference,
                    first.sku,
                    first.purchased_quantity,
                    first.eta,
                )
            )
        async for row in rows:
            if row.reference is not None and row.purchased_quantity is not None:
                batches.append(
                    model.Batch(
                        row.reference,
                        row.sku,
                        row.purchased_quantity,
                        row.eta,
                    )
                )
        return model.Product(
            sku=first.sku,
            batches=batches,
            version_number=first.version_number,
        )

    async def list(self) -> AsyncIterator[model.Product]:
        async for row in self.querier.all_products():
            if row.products is None:
                raise StopAsyncIteration

            batches: list[model.Batch] = []
            if row.batches is not None:
                batches.append(
                    model.Batch(
                        row.batches.reference,
                        row.batches.sku,
                        row.batches._purchased_quantity,
                        row.batches.eta,
                    )
                )
            yield model.Product(
                sku=row.products.sku,
                batches=batches,
                version_number=row.products.version_number,
            )
