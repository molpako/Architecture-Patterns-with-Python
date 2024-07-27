import abc


import model
from backend.query import Querier
from backend.models import Batch


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class BackendRepository(AbstractRepository):
    def __init__(self, querier: Querier):
        self.querier = querier

    def add(self, batch) -> None:
        self.querier.add_batch(
            reference=batch.reference,
            sku=batch.sku,
            _purchased_quantity=batch._purchased_quantity,
            eta=batch.eta,
        )

    def get(self, reference) -> Batch | None:
        return self.querier.get_batch(reference=reference)

    def list(self) -> list[Batch]:
        return list(self.querier.all_batches())
