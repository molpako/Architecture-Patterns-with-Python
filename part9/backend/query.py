# Code generated by sqlc. DO NOT EDIT.
# versions:
#   sqlc v1.27.0
# source: query.sql
import datetime
from typing import AsyncIterator, Iterator, Optional

import sqlalchemy
import sqlalchemy.ext.asyncio

from backend import models


ADD_ALLOCATION = """-- name: add_allocation \\:one
INSERT INTO allocations (
    orderline_id, batch_id
) VALUES (
    :p1, :p2
) RETURNING id, orderline_id, batch_id
"""


ADD_ORDER_LINE = """-- name: add_order_line \\:one
INSERT INTO order_lines (
    sku, qty, orderid
) VALUES (
    :p1, :p2, :p3
) RETURNING id, sku, qty, orderid
"""


CLEAR_ORDER_LINES = """-- name: clear_order_lines \\:exec
DELETE FROM order_lines
USING allocations
WHERE order_lines.id = allocations.orderline_id
AND allocations.batch_id = :p1
"""


CREATE_OR_UPDATE_BATCH = """-- name: create_or_update_batch \\:one
INSERT INTO batches (
    reference, sku, purchased_quantity, eta
) VALUES (
    :p1, :p2, :p3, :p4
) ON CONFLICT (reference)
DO UPDATE SET sku = :p2, purchased_quantity = :p3, eta = :p4
RETURNING id, reference, sku, purchased_quantity, eta
"""


CREATE_OR_UPDATE_PRODUCT = """-- name: create_or_update_product \\:one
INSERT INTO products (
    sku, version_number
) VALUES (
    :p1, :p2
) ON CONFLICT (sku)
DO UPDATE SET version_number = :p2
RETURNING sku, version_number
"""


GET_BATCH = """-- name: get_batch \\:many
SELECT id, reference, sku, purchased_quantity, eta
FROM batches
WHERE sku = :p1
"""


GET_ORDERLINES = """-- name: get_orderlines \\:many
SELECT order_lines.id, order_lines.sku, order_lines.qty, order_lines.orderid
FROM order_lines
JOIN allocations ON order_lines.id = allocations.orderline_id
JOIN batches ON allocations.batch_id = batches.id
WHERE batches.id = :p1
"""


GET_PRODUCT = """-- name: get_product \\:one
SELECT sku, version_number
FROM products
WHERE products.sku = :p1
"""


GET_PRODUCT_BY_BATCHREF = """-- name: get_product_by_batchref \\:one
SELECT products.sku, products.version_number
FROM products
JOIN batches ON products.sku = batches.sku
WHERE batches.reference = :p1
"""


class Querier:
    def __init__(self, conn: sqlalchemy.engine.Connection):
        self._conn = conn

    def add_allocation(self, *, orderline_id: Optional[int], batch_id: Optional[int]) -> Optional[models.Allocation]:
        row = self._conn.execute(sqlalchemy.text(ADD_ALLOCATION), {"p1": orderline_id, "p2": batch_id}).first()
        if row is None:
            return None
        return models.Allocation(
            id=row[0],
            orderline_id=row[1],
            batch_id=row[2],
        )

    def add_order_line(self, *, sku: Optional[str], qty: int, orderid: Optional[str]) -> Optional[models.OrderLine]:
        row = self._conn.execute(sqlalchemy.text(ADD_ORDER_LINE), {"p1": sku, "p2": qty, "p3": orderid}).first()
        if row is None:
            return None
        return models.OrderLine(
            id=row[0],
            sku=row[1],
            qty=row[2],
            orderid=row[3],
        )

    def clear_order_lines(self, *, batch_id: Optional[int]) -> None:
        self._conn.execute(sqlalchemy.text(CLEAR_ORDER_LINES), {"p1": batch_id})

    def create_or_update_batch(self, *, reference: Optional[str], sku: str, purchased_quantity: int, eta: Optional[datetime.date]) -> Optional[models.Batch]:
        row = self._conn.execute(sqlalchemy.text(CREATE_OR_UPDATE_BATCH), {
            "p1": reference,
            "p2": sku,
            "p3": purchased_quantity,
            "p4": eta,
        }).first()
        if row is None:
            return None
        return models.Batch(
            id=row[0],
            reference=row[1],
            sku=row[2],
            purchased_quantity=row[3],
            eta=row[4],
        )

    def create_or_update_product(self, *, sku: str, version_number: int) -> Optional[models.Product]:
        row = self._conn.execute(sqlalchemy.text(CREATE_OR_UPDATE_PRODUCT), {"p1": sku, "p2": version_number}).first()
        if row is None:
            return None
        return models.Product(
            sku=row[0],
            version_number=row[1],
        )

    def get_batch(self, *, sku: str) -> Iterator[models.Batch]:
        result = self._conn.execute(sqlalchemy.text(GET_BATCH), {"p1": sku})
        for row in result:
            yield models.Batch(
                id=row[0],
                reference=row[1],
                sku=row[2],
                purchased_quantity=row[3],
                eta=row[4],
            )

    def get_orderlines(self, *, id: int) -> Iterator[models.OrderLine]:
        result = self._conn.execute(sqlalchemy.text(GET_ORDERLINES), {"p1": id})
        for row in result:
            yield models.OrderLine(
                id=row[0],
                sku=row[1],
                qty=row[2],
                orderid=row[3],
            )

    def get_product(self, *, sku: str) -> Optional[models.Product]:
        row = self._conn.execute(sqlalchemy.text(GET_PRODUCT), {"p1": sku}).first()
        if row is None:
            return None
        return models.Product(
            sku=row[0],
            version_number=row[1],
        )

    def get_product_by_batchref(self, *, reference: Optional[str]) -> Optional[models.Product]:
        row = self._conn.execute(sqlalchemy.text(GET_PRODUCT_BY_BATCHREF), {"p1": reference}).first()
        if row is None:
            return None
        return models.Product(
            sku=row[0],
            version_number=row[1],
        )


class AsyncQuerier:
    def __init__(self, conn: sqlalchemy.ext.asyncio.AsyncConnection):
        self._conn = conn

    async def add_allocation(self, *, orderline_id: Optional[int], batch_id: Optional[int]) -> Optional[models.Allocation]:
        row = (await self._conn.execute(sqlalchemy.text(ADD_ALLOCATION), {"p1": orderline_id, "p2": batch_id})).first()
        if row is None:
            return None
        return models.Allocation(
            id=row[0],
            orderline_id=row[1],
            batch_id=row[2],
        )

    async def add_order_line(self, *, sku: Optional[str], qty: int, orderid: Optional[str]) -> Optional[models.OrderLine]:
        row = (await self._conn.execute(sqlalchemy.text(ADD_ORDER_LINE), {"p1": sku, "p2": qty, "p3": orderid})).first()
        if row is None:
            return None
        return models.OrderLine(
            id=row[0],
            sku=row[1],
            qty=row[2],
            orderid=row[3],
        )

    async def clear_order_lines(self, *, batch_id: Optional[int]) -> None:
        await self._conn.execute(sqlalchemy.text(CLEAR_ORDER_LINES), {"p1": batch_id})

    async def create_or_update_batch(self, *, reference: Optional[str], sku: str, purchased_quantity: int, eta: Optional[datetime.date]) -> Optional[models.Batch]:
        row = (await self._conn.execute(sqlalchemy.text(CREATE_OR_UPDATE_BATCH), {
            "p1": reference,
            "p2": sku,
            "p3": purchased_quantity,
            "p4": eta,
        })).first()
        if row is None:
            return None
        return models.Batch(
            id=row[0],
            reference=row[1],
            sku=row[2],
            purchased_quantity=row[3],
            eta=row[4],
        )

    async def create_or_update_product(self, *, sku: str, version_number: int) -> Optional[models.Product]:
        row = (await self._conn.execute(sqlalchemy.text(CREATE_OR_UPDATE_PRODUCT), {"p1": sku, "p2": version_number})).first()
        if row is None:
            return None
        return models.Product(
            sku=row[0],
            version_number=row[1],
        )

    async def get_batch(self, *, sku: str) -> AsyncIterator[models.Batch]:
        result = await self._conn.stream(sqlalchemy.text(GET_BATCH), {"p1": sku})
        async for row in result:
            yield models.Batch(
                id=row[0],
                reference=row[1],
                sku=row[2],
                purchased_quantity=row[3],
                eta=row[4],
            )

    async def get_orderlines(self, *, id: int) -> AsyncIterator[models.OrderLine]:
        result = await self._conn.stream(sqlalchemy.text(GET_ORDERLINES), {"p1": id})
        async for row in result:
            yield models.OrderLine(
                id=row[0],
                sku=row[1],
                qty=row[2],
                orderid=row[3],
            )

    async def get_product(self, *, sku: str) -> Optional[models.Product]:
        row = (await self._conn.execute(sqlalchemy.text(GET_PRODUCT), {"p1": sku})).first()
        if row is None:
            return None
        return models.Product(
            sku=row[0],
            version_number=row[1],
        )

    async def get_product_by_batchref(self, *, reference: Optional[str]) -> Optional[models.Product]:
        row = (await self._conn.execute(sqlalchemy.text(GET_PRODUCT_BY_BATCHREF), {"p1": reference})).first()
        if row is None:
            return None
        return models.Product(
            sku=row[0],
            version_number=row[1],
        )
