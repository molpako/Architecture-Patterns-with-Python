from typing import Type, Callable

from domain import events
from . import handlers

from . import unit_of_work


async def handle(event: events.Event, uow: unit_of_work.AbstractUnitOfWork) -> list:
    results = []
    queue = [event]
    while queue:
        event = queue.pop(0)
        for handler in HANDLERS[type(event)]:
            results.append(await handler(event, uow=uow))
            queue.extend(uow.collect_new_events())
    return results


HANDLERS: dict[Type[events.Event], list[Callable]] = {
    events.BatchCreated: [handlers.add_batch],
    events.BatchQuantityChanged: [handlers.change_batch_quantity],
    events.AllocationRequired: [handlers.allocate],
    events.OutOfStock: [handlers.send_out_of_stock_notification],
}
