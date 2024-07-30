import abc
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncConnection

import model
from backend.query import AsyncQuerier


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, batch: model.Batch) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, reference) -> model.Batch:
        raise NotImplementedError

    @abc.abstractmethod
    async def list(self) -> AsyncIterator[model.Batch]:
        if False:
            yield 1


class BackendRepository(AbstractRepository):
    def __init__(self, conn: AsyncConnection):
        self.querier = AsyncQuerier(conn)

    def mapper(self, batch) -> model.Batch:
        return model.Batch(
            str(batch.reference),
            str(batch.sku),
            batch._purchased_quantity,
            batch.eta,
        )

    async def add(self, batch) -> None:
        await self.querier.add_batch(
            reference=batch.reference,
            sku=batch.sku,
            _purchased_quantity=batch._purchased_quantity,
            eta=batch.eta,
        )

    async def get(self, reference) -> model.Batch:
        result = await self.querier.get_batch(reference=reference)
        if result is None:
            raise Exception(f"Batch {reference} not found")
        return self.mapper(result)

    async def list(self) -> AsyncIterator[model.Batch]:
        async for batch in self.querier.all_batches():
            yield self.mapper(batch)
