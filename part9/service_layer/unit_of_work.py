from __future__ import annotations
import abc
from typing import Generator

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from adapters import repository
from domain import events

import config


class AbstractUnitOfWork(abc.ABC):
    products: repository.AbstractProductRepository

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.rollback()

    async def commit(self):
        await self._commit()

    def collect_new_events(self) -> Generator[events.Event]:
        for product in self.products.seen:
            while product.events:
                yield product.events.pop(0)

    @abc.abstractmethod
    async def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self):
        raise NotImplementedError


async_engine = create_async_engine(
    config.get_postgres_uri(),
    future=True,
    echo=True,
)


class BackendUnitOfWork(AbstractUnitOfWork):
    def __init__(self, engine: AsyncEngine = async_engine):
        self.connection = engine.connect()

    async def __aenter__(self):
        self.connection = await self.connection.start()
        self.products = repository.BackendRepository(self.connection)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.connection.close()

    async def _commit(self):
        for product in self.products.seen:
            await self.products.update(product)
        await self.connection.commit()

    async def rollback(self):
        await self.connection.rollback()
