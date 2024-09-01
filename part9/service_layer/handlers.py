from __future__ import annotations
from typing import TYPE_CHECKING

from domain import model, events
from adapters import email

if TYPE_CHECKING:
    from . import unit_of_work


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


async def allocate(
    event: events.AllocationRequired, uow: unit_of_work.AbstractUnitOfWork
) -> str:
    async with uow:
        product = await uow.products.get(sku=event.sku)
        if product is None:
            raise InvalidSku(f"Invalid sku {event.sku}")
        line = model.OrderLine(event.orderid, event.sku, event.qty)
        batchref = product.allocate(line)
        await uow.commit()
    return batchref if batchref else ""


async def add_batch(
    event: events.BatchCreated,
    uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    async with uow:
        product = await uow.products.get(sku=event.sku)
        if product is None:
            product = model.Product(event.sku, batches=[])
            await uow.products.add(product)

        batch = model.Batch(event.ref, event.sku, event.qty, event.eta)
        product.batches.append(batch)
        await uow.commit()


def send_out_of_stock_notification(event: events.OutOfStock):
    email.send_mail(
        "stock@made.com",
        f"Out of stock for {event.sku}",
    )
