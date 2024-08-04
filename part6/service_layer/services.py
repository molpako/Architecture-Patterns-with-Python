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
        batches: list[model.Batch] = [i async for i in uow.batches.list()]
        if not is_valid_sku(sku, batches):
            raise InvalidSku(f"Invalid sku {sku}")
        batchref = model.allocate(model.OrderLine(orderid, sku, qty), batches)
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
        await uow.batches.add(model.Batch(ref, sku, qty, eta))
        await uow.commit()
