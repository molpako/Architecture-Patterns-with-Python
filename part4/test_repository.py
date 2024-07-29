import model
from backend import query
import repository


# repository のテストは querier を抽象化することにより行う？
def test_repository_can_save_a_batch(session):
    batch = model.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = repository.BackendRepository(query.Querier(session))
    repo.add(batch)  # テストのターゲット
    session.commit()

    rows = list(
        session.execute(
            'SELECT reference, sku, _purchased_quantity, eta FROM "batches"'
        )
    )
    assert rows == [("batch1", "RUSTY-SOAPDISH", 100, None)]
