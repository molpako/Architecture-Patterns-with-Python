"""
Presentation Layer
"""

from dataclasses import dataclass
from datetime import datetime
import logging
import sys


from fastapi import FastAPI, HTTPException, status


import domain.model as model
from service_layer import services, unit_of_work


app = FastAPI()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@app.post("/allocate", status_code=status.HTTP_201_CREATED)
async def allocate_endpoint(item: model.OrderLine):
    try:
        batchref = await services.allocate(
            item.orderid, item.sku, item.qty, unit_of_work.BackendUnitOfWork()
        )
    except services.InvalidSku as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"batchref": batchref}


@dataclass
class AddBatchRequest:
    ref: str
    sku: str
    qty: int
    eta: str | None


@app.post("/batches", status_code=status.HTTP_201_CREATED)
async def add_batch(batch: AddBatchRequest):
    eta_date = datetime.fromisoformat(batch.eta).date() if batch.eta else None
    await services.add_batch(
        batch.ref,
        batch.sku,
        batch.qty,
        eta_date,  # type: _Date | Unbound
        unit_of_work.BackendUnitOfWork(),
    )
    return "OK"


def generate(): ...
