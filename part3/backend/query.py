# Code generated by sqlc. DO NOT EDIT.
# versions:
#   sqlc v1.26.0
# source: query.sql
import datetime
from typing import AsyncIterator, Iterator, Optional

import sqlalchemy
import sqlalchemy.ext.asyncio

from backend import models


ADD_BATCH = """-- name: add_batch \\:one
INSERT INTO batches (
    reference, sku, _purchased_quantity, eta
) VALUES (
    :p1, :p2, :p3, :p4
) RETURNING id, reference, sku, _purchased_quantity, eta
"""


ALL_BATCHES = """-- name: all_batches \\:many
SELECT id, reference, sku, _purchased_quantity, eta
FROM batches
"""


GET_BATCH = """-- name: get_batch \\:one
SELECT id, reference, sku, _purchased_quantity, eta
FROM batches
WHERE reference = :p1
"""


class Querier:
    def __init__(self, conn: sqlalchemy.engine.Connection):
        self._conn = conn

    def add_batch(self, *, reference: Optional[str], sku: Optional[str], _purchased_quantity: int, eta: Optional[datetime.date]) -> Optional[models.Batch]:
        row = self._conn.execute(sqlalchemy.text(ADD_BATCH), {
            "p1": reference,
            "p2": sku,
            "p3": _purchased_quantity,
            "p4": eta,
        }).first()
        if row is None:
            return None
        return models.Batch(
            id=row[0],
            reference=row[1],
            sku=row[2],
            _purchased_quantity=row[3],
            eta=row[4],
        )

    def all_batches(self) -> Iterator[models.Batch]:
        result = self._conn.execute(sqlalchemy.text(ALL_BATCHES))
        for row in result:
            yield models.Batch(
                id=row[0],
                reference=row[1],
                sku=row[2],
                _purchased_quantity=row[3],
                eta=row[4],
            )

    def get_batch(self, *, reference: Optional[str]) -> Optional[models.Batch]:
        row = self._conn.execute(sqlalchemy.text(GET_BATCH), {"p1": reference}).first()
        if row is None:
            return None
        return models.Batch(
            id=row[0],
            reference=row[1],
            sku=row[2],
            _purchased_quantity=row[3],
            eta=row[4],
        )


class AsyncQuerier:
    def __init__(self, conn: sqlalchemy.ext.asyncio.AsyncConnection):
        self._conn = conn

    async def add_batch(self, *, reference: Optional[str], sku: Optional[str], _purchased_quantity: int, eta: Optional[datetime.date]) -> Optional[models.Batch]:
        row = (await self._conn.execute(sqlalchemy.text(ADD_BATCH), {
            "p1": reference,
            "p2": sku,
            "p3": _purchased_quantity,
            "p4": eta,
        })).first()
        if row is None:
            return None
        return models.Batch(
            id=row[0],
            reference=row[1],
            sku=row[2],
            _purchased_quantity=row[3],
            eta=row[4],
        )

    async def all_batches(self) -> AsyncIterator[models.Batch]:
        result = await self._conn.stream(sqlalchemy.text(ALL_BATCHES))
        async for row in result:
            yield models.Batch(
                id=row[0],
                reference=row[1],
                sku=row[2],
                _purchased_quantity=row[3],
                eta=row[4],
            )

    async def get_batch(self, *, reference: Optional[str]) -> Optional[models.Batch]:
        row = (await self._conn.execute(sqlalchemy.text(GET_BATCH), {"p1": reference})).first()
        if row is None:
            return None
        return models.Batch(
            id=row[0],
            reference=row[1],
            sku=row[2],
            _purchased_quantity=row[3],
            eta=row[4],
        )
