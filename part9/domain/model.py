from dataclasses import dataclass
from datetime import date

from domain import events


@dataclass(frozen=True)
class OrderLine:
    """値オブジェクト"""

    orderid: str
    sku: str
    qty: int


class Batch:
    """エンティティ"""

    def __init__(self, ref: str, sku: str, qty: int, eta: date | None):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations: set[OrderLine] = set()

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        """辞書検索の高速化などに使われる hash
        エンティティクラスに実装する場合は reference などの不変な値に基づくのが一般的"""
        return hash(self.reference)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def __repr__(self):
        return f"<Batch {self.reference}>"

    def allocate(self, line: OrderLine) -> None:
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate_one(self) -> OrderLine:
        return self._allocations.pop()

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty


# Product is an aggregate object that we treat as a single unit for the purpose of data changes.
class Product:
    def __init__(self, sku: str, batches: list[Batch], version_number: int = 0):
        self.sku = sku
        self.batches = batches
        self.version_number = version_number
        self.events: list[events.Event] = []

    def __eq__(self, other):
        if not isinstance(other, Product):
            return False
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(self.__dict__.values())

    def __repr__(self):
        return f"{self.sku=}, {self.version_number=}, batches={[b.reference for b in self.batches]}"

    def allocate(self, line: OrderLine) -> str | None:
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
        except StopIteration:
            self.events.append(events.OutOfStock(sku=line.sku))
            return None
        batch.allocate(line)
        self.version_number += 1
        return batch.reference

    def change_batch_quantity(self, ref: str, qty: int):
        batch = next(b for b in self.batches if b.reference == ref)
        batch._purchased_quantity = qty
        while batch.available_quantity < 0:
            line = batch.deallocate_one()
            self.events.append(
                events.AllocationRequired(line.orderid, line.sku, line.qty)
            )
