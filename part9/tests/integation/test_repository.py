import pytest
from adapters import repository
from domain import model
from service_layer import unit_of_work
from sqlalchemy.sql import text


async def insert_batch(async_conn, ref, sku, qty, eta, product_version=1):
    await async_conn.execute(
        text(
            "INSERT INTO products (sku, version_number) VALUES (:sku, :version) ON CONFLICT (sku) DO NOTHING"
        ),
        dict(sku=sku, version=product_version),
    )
    await async_conn.execute(
        text(
            "INSERT INTO batches (reference, sku, purchased_quantity, eta)"
            " VALUES (:ref, :sku, :qty, :eta) ON CONFLICT (reference)"
            " DO UPDATE SET sku = :sku, purchased_quantity = :qty, eta = :eta"
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


@pytest.mark.asyncio
async def test_get_by_batchref(async_conn):
    print(f"{async_conn=}")
    repo = repository.BackendRepository(async_conn)
    b1 = model.Batch(ref="b1", sku="sku1", qty=100, eta=None)
    b2 = model.Batch(ref="b2", sku="sku1", qty=100, eta=None)
    b3 = model.Batch(ref="b3", sku="sku2", qty=100, eta=None)
    p1 = model.Product(sku="sku1", batches=[b1, b2])
    p2 = model.Product(sku="sku2", batches=[b3])
    await repo.add(p1)
    await repo.add(p2)
    got1 = await repo.get_by_batchref("b2")
    print(f"{got1=}")
    print(f"{p1=}")
    print(f"{got1.__dict__=}")
    print(f"{p1.__dict__=}")
    assert got1 == p1
    assert await repo.get_by_batchref("b3") == p2
