import model
import repository


class InvalidSku(Exception):
    pass


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


async def allocate(
    line: model.OrderLine, repo: repository.BackendRepository, conn
) -> str:
    batches: list[model.Batch] = [r async for r in repo.list()]
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.allocate(line, batches)
    conn.commit()
    return batchref
