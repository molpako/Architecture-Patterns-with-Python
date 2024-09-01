"""
Presentation Layer
"""

from dataclasses import dataclass
from datetime import datetime
import logging
import sys


from fastapi import FastAPI, HTTPException, status


from domain import events
from service_layer import handlers, unit_of_work


app = FastAPI()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@app.post("/allocate", status_code=status.HTTP_201_CREATED)
async def allocate_endpoint(item: events.AllocationRequired):
    try:
        batchref = await handlers.allocate(
            item,
            unit_of_work.BackendUnitOfWork(),
        )
    except handlers.InvalidSku as exc:
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
    await handlers.add_batch(
        events.BatchCreated(batch.ref, batch.sku, batch.qty, eta_date),
        unit_of_work.BackendUnitOfWork(),
    )
    return "OK"
