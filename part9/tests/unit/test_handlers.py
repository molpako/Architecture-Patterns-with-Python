from datetime import date, timedelta

import pytest

from adapters import repository
from domain import events
from service_layer import handlers, unit_of_work, messagebus


today = date.today()
tomorrow = today + timedelta(days=1)


class FakeRepository(repository.AbstractProductRepository):
    def __init__(self, products):
        super().__init__()
        self._products = set(products)

    async def add(self, product):
        self._products.add(product)

    async def _get(self, sku):
        return next((p for p in self._products if p.sku == sku), None)

    async def update(self, product) -> None:
        pass

    async def aiter(self):
        for product in self._products:
            yield product

    async def list(self):
        async for product in aiter(self.aiter()):
            yield product


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    async def _commit(self):
        self.committed = True

    async def rollback(self):
        pass


@pytest.mark.asyncio
async def test_returns_allocation():
    uow = FakeUnitOfWork()
    await messagebus.handle(
        events.BatchCreated("batch1", "COMPLICATED-LAMP", 100, None), uow
    )
    results = await messagebus.handle(
        events.AllocationRequired("o1", "COMPLICATED-LAMP", 10), uow
    )
    assert results.pop(0) == "batch1"


@pytest.mark.asyncio
async def test_error_for_invalid_sku():
    uow = FakeUnitOfWork()
    await handlers.add_batch(
        events.BatchCreated(
            "b1",
            "AREALSKU",
            100,
            None,
        ),
        uow,
    )
    with pytest.raises(handlers.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        await handlers.allocate(
            events.AllocationRequired(
                "o1",
                "NONEXISTENTSKU",
                10,
            ),
            uow,
        )


@pytest.mark.asyncio
async def test_add_batch_for_new_product():
    uow = FakeUnitOfWork()
    await messagebus.handle(
        events.BatchCreated("b1", "CRUNCHY-ARMCHAIR", 100, None), uow
    )
    assert await uow.products.get("CRUNCHY-ARMCHAIR") is not None
    assert uow.committed
