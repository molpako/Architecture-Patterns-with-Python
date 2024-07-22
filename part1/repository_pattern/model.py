from dataclasses import dataclass
from datetime import date


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

    def allocate(self, line: OrderLine) -> None:
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine) -> None:
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return False
        return other.reference == self.reference

    def __hash__(self):
        """辞書検索の高速化などに使われる hash
        エンティティクラスに実装する場合は reference などの不変な値に基づくのが一般的"""
        return hash(self.reference)


def allocate(line: OrderLine, bathces: list[Batch]) -> str:
    batch = next(b for b in sorted(bathces) if b.can_allocate(line))
    batch.allocate(line)
    return batch.reference
