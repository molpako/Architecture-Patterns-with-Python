from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: date | None):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self.available_quantity = qty

    def allocate(self, line: OrderLine):
        # ドメインモデルの場合、期待される引数が何であるかを明確にしたり、文書化するのに役立つことがあります。 読みやすさの点で支払う代償は高すぎると判断するかもしれません。
        self.available_quantity -= line.qty

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty

    def deallocate(self, line: OrderLine):
        self.available_quantity += line.qty
