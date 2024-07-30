"""
Presentation Layer
"""

import logging
import sys


from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine

import config
import model
import repository
import services


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
    line = model.OrderLine(item.orderid, item.sku, item.qty)

    try:
        batchref = await services.allocate(line, repo, conn)
    except (model.OutOfStock, services.InvalidSku) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"batchref": batchref}
