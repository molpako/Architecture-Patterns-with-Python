import pytest
from domain import model
from service_layer import unit_of_work
from sqlalchemy.sql import text


async def insert_batch(async_conn, ref, sku, qty, eta, product_version=1):
    await async_conn.execute(
        text("INSERT INTO products (sku, version_number) VALUES (:sku, :version)"),
        dict(sku=sku, version=product_version),
    )
    await async_conn.execute(
        text(
            "INSERT INTO batches (reference, sku, purchased_quantity, eta)"
            " VALUES (:ref, :sku, :qty, :eta)"
        ),
        dict(ref=ref, sku=sku, qty=qty, eta=eta),
    )


async def get_allocated_batch_ref(async_conn, orderid, sku):
    [[orderlineid]] = await async_conn.execute(
        text("SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku"),
        dict(orderid=orderid, sku=sku),
    )
    [[batchref]] = await async_conn.execute(
        text(
            "SELECT b.reference FROM allocations JOIN batches AS b ON batch_id = b.id"
            " WHERE orderline_id=:orderlineid"
        ),
        dict(orderlineid=orderlineid),
    )
    return batchref


@pytest.mark.asyncio
async def test_uow_can_retrieve_a_batch_and_allocate_to_it(async_engine):
    async with async_engine.begin() as async_conn:
        await insert_batch(async_conn, "batch1", "HIPSTER-WORKBENCH", 100, None)
        await async_conn.commit()

    uow = unit_of_work.BackendUnitOfWork(async_engine)
    async with uow:
        product = await uow.products.get(sku="HIPSTER-WORKBENCH")
        line = model.OrderLine("o1", "HIPSTER-WORKBENCH", 10)
        product.allocate(line)
        await uow.commit()

    async with async_engine.begin() as async_conn:
        batchref = await get_allocated_batch_ref(async_conn, "o1", "HIPSTER-WORKBENCH")
    assert batchref == "batch1"
