from typing import Type, Callable

from domain import events
from . import handlers


def handle(event: events.Event):
    for handler in HANDLERS[type(event)]:
        handler(event)


HANDLERS: dict[Type[events.Event], list[Callable]] = {
    events.OutOfStock: [handlers.send_out_of_stock_notification],
}
