import pytest
from domain import model
from adapters import repository

from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import text


@pytest.mark.asyncio
async def test_repository_can_save_a_batch(async_conn: AsyncConnection):
    batch = model.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = repository.BackendRepository(async_conn)
    await repo.add(batch)  # テストのターゲット
    await async_conn.commit()

    rows = await async_conn.execute(
        text('SELECT reference, sku, _purchased_quantity, eta FROM "batches"')
    )
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]
