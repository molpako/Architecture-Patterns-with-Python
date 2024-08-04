import abc
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from adapters import repository

import config


class AbstractUnitOfWork(abc.ABC):
    batches: repository.AbstractRepository

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.rollback()

    @abc.abstractmethod
    async def commit(self):
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
        self.batches = repository.BackendRepository(self.connection)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.connection.close()

    async def commit(self):
        await self.connection.commit()

    async def rollback(self):
        await self.connection.rollback()
