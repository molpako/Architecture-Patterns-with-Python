"""
Presentation Layer
"""

from dataclasses import dataclass
from datetime import datetime
import logging
import sys


from fastapi import FastAPI, HTTPException, status, Depends
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

app = FastAPI()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


async def connection():
    async with async_engine.connect() as conn:
        yield conn


@app.post("/allocate", status_code=status.HTTP_201_CREATED)
async def allocate_endpoint(item: model.OrderLine, conn=Depends(connection)):
    logger.debug(f"postgres uri: {config.get_postgres_uri()}")
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


@app.post("/batches", status_code=status.HTTP_201_CREATED)
async def add_batch(item: AddBatchRequest, conn=Depends(connection)):
    repo = repository.BackendRepository(conn)
    eta_date = datetime.fromisoformat(item.eta).date() if item.eta else None
    await services.add_batch(
        item.ref,
        item.sku,
        item.qty,
        eta_date,  # type: _Date | Unbound
        repo,
        conn,
    )

    return "OK"
