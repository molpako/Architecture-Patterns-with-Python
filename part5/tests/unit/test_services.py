from datetime import date, timedelta

import pytest

from domain import model
from adapters import repository
from service_layer import services

today = date.today()
tomorrow = today + timedelta(days=1)


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    async def add(self, batch):
        self._batches.add(batch)

    async def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    async def aiter(self):
        for batch in self._batches:
            yield batch

    async def list(self):
        async for batch in aiter(self.aiter()):
            yield batch


class FakeSession:
    committed = False

    async def commit(self):
        self.committed = True


@pytest.mark.asyncio
async def test_returns_allocation():
    batch = model.Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])
    result = await services.allocate("o1", "COMPLICATED-LAMP", 10, repo, FakeSession())
    assert result == "b1"


@pytest.mark.asyncio
async def test_error_for_invalid_sku():
    batch = model.Batch("b1", "AREALSKU", 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        await services.allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())


@pytest.mark.asyncio
async def test_commits():
    batch = model.Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    await services.allocate("o1", "OMINOUS-MIRROR", 10, repo, session)
    assert session.committed is True


@pytest.mark.asyncio
async def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = model.Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = model.Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tomorrow)
    repo = FakeRepository([in_stock_batch, shipment_batch])
    session = FakeSession()

    await services.allocate("oref", "RETRO-CLOCK", 10, repo, session)

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100
