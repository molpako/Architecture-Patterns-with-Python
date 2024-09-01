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

    async def _get_by_batchref(self, batchref):
        return next(
            (p for p in self._products for b in p.batches if b.reference == batchref),
            None,
        )

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


class TestChangeBatchQuantity:
    @pytest.mark.asyncio
    async def test_changes_available_quantity(self):
        uow = FakeUnitOfWork()
        await messagebus.handle(
            events.BatchCreated("batch1", "ADORABLE-SETTEE", 100, None), uow
        )
        [batch] = (await uow.products.get(sku="ADORABLE-SETTEE")).batches
        assert batch.available_quantity == 100

        await messagebus.handle(events.BatchQuantityChanged("batch1", 50), uow)

        assert batch.available_quantity == 50

    @pytest.mark.asyncio
    async def test_reallocates_if_necessary(self):
        uow = FakeUnitOfWork()
        event_history = [
            events.BatchCreated("batch1", "INDIFFERENT-TABLE", 50, None),
            events.BatchCreated("batch2", "INDIFFERENT-TABLE", 50, date.today()),
            events.AllocationRequired("order1", "INDIFFERENT-TABLE", 20),
            events.AllocationRequired("order2", "INDIFFERENT-TABLE", 20),
        ]
        for e in event_history:
            await messagebus.handle(e, uow)
        [batch1, batch2] = (await uow.products.get(sku="INDIFFERENT-TABLE")).batches
        assert batch1.available_quantity == 10
        assert batch2.available_quantity == 50

        await messagebus.handle(events.BatchQuantityChanged("batch1", 25), uow)

        # order1 or order2 will be deallocated, so we'll have 25 - 20
        assert batch1.available_quantity == 5
        # and 20 will be reallocated to the next batch
        assert batch2.available_quantity == 30
