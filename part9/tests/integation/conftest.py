import pytest_asyncio
import pytest
from sqlalchemy.ext.asyncio import create_async_engine

import config


# Considering using https://github.com/testcontainers/testcontainers-python
@pytest.fixture(scope="session")
def async_engine():
    print(config.get_postgres_uri())
    return create_async_engine(config.get_postgres_uri())


@pytest_asyncio.fixture
async def async_conn(async_engine):
    async with async_engine.connect() as async_conn:
        yield async_conn
