from domain import model
from adapters import repository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


async def allocate(
    line: model.OrderLine, repo: repository.AbstractRepository, conn
) -> str:
    batches: list[model.Batch] = [i async for i in repo.list()]
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.allocate(line, batches)
    await conn.commit()
    return batchref
