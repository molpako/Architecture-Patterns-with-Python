"""
Presentation Layer
"""

from dataclasses import dataclass
from datetime import datetime
import logging
import sys


from fastapi import FastAPI, HTTPException, status
from sqlalchemy.ext.asyncio import create_async_engine

import config
import domain.model as model
from adapters import repository
from service_layer import services


async_engine = create_async_engine(
    config.get_postgres_uri(),
    future=True,
    echo=True,
)

async_conn = async_engine.connect()


app = FastAPI()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@app.post("/allocate")
async def allocate_endpoint(item: model.OrderLine):
    logger.debug(f"postgres uri: {config.get_postgres_uri()}")
    conn = await async_conn.start()
    repo = repository.BackendRepository(conn)
    try:
        batchref = await services.allocate(item.orderid, item.sku, item.qty, repo, conn)
    except (model.OutOfStock, services.InvalidSku) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"batchref": batchref}


@dataclass
class AddBatchRequest:
    ref: str
    sku: str
    qty: int
    eta: str | None


@app.post("/add_batch", status_code=status.HTTP_201_CREATED)
async def add_batch(item: AddBatchRequest):
    conn = await async_conn.start()
    repo = repository.BackendRepository(conn)
    if item.eta is not None:
        eta_date = datetime.fromisoformat(item.eta).date()
    await services.add_batch(
        item.ref,
        item.sku,
        item.qty,
        eta_date,  # type: _Date | Unbound
        repo,
        conn,
    )
    return "OK"
