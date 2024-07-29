import abc
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncConnection

import model
from backend.models import Batch
from backend.query import AsyncQuerier


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class BackendRepository(AbstractRepository):
    def __init__(self, conn: AsyncConnection):
        self.querier = AsyncQuerier(conn)

    async def add(self, batch) -> None:
        await self.querier.add_batch(
            reference=batch.reference,
            sku=batch.sku,
            _purchased_quantity=batch._purchased_quantity,
            eta=batch.eta,
        )

    async def get(self, reference) -> Batch | None:
        return await self.querier.get_batch(reference=reference)

    async def list(self) -> AsyncIterator[model.Batch]:
        async for batch in self.querier.all_batches():
            yield model.Batch(
                str(batch.reference),
                str(batch.sku),
                batch._purchased_quantity,
                batch.eta,
            )
