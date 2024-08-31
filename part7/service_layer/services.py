from datetime import date

from domain import model
from service_layer import unit_of_work


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


async def allocate(
    orderid: str, sku: str, qty: int, uow: unit_of_work.AbstractUnitOfWork
) -> str:
    async with uow:
        product = await uow.products.get(sku=sku)
        if product is None:
            raise InvalidSku(f"Invalid sku {sku}")
        line = model.OrderLine(orderid, sku, qty)
        batchref = product.allocate(line)
        await uow.commit()
    return batchref


async def add_batch(
    ref: str,
    sku: str,
    qty: int,
    eta: date | None,
    uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    async with uow:
        product = await uow.products.get(sku=sku)
        if product is None:
            product = model.Product(sku, batches=[])
            await uow.products.add(product)

        batch = model.Batch(ref, sku, qty, eta)
        product.batches.append(batch)
        await uow.commit()
