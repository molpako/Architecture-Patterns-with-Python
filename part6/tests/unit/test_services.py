from datetime import date, timedelta

import pytest

from adapters import repository
from service_layer import services, unit_of_work

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


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.batches = FakeRepository([])
        self.committed = False

    async def commit(self):
        self.committed = True

    async def rollback(self):
        pass


@pytest.mark.asyncio
async def test_returns_allocation():
    uow = FakeUnitOfWork()
    await services.add_batch("b1", "COMPLICATED-LAMP", 100, None, uow)
    result = await services.allocate("o1", "COMPLICATED-LAMP", 10, uow)
    assert result == "b1"


@pytest.mark.asyncio
async def test_error_for_invalid_sku():
    uow = FakeUnitOfWork()
    await services.add_batch(
        "b1",
        "AREALSKU",
        100,
        None,
        uow,
    )
    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        await services.allocate("o1", "NONEXISTENTSKU", 10, uow)


@pytest.mark.asyncio
async def test_commits():
    uow = FakeUnitOfWork()
    await services.add_batch("b1", "OMINOUS-MIRROR", 100, None, uow)
    await services.allocate("o1", "OMINOUS-MIRROR", 10, uow)
    assert uow.committed is True


@pytest.mark.asyncio
async def test_add_batch():
    uow = FakeUnitOfWork()
    await services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)
    assert await uow.batches.get("b1") is not None
    assert uow.committed
