from app.db.session import get_db_engine
from app.db.seed_data import seed_database
from app.core.executor import SQLExecutor


def test_executor_valid_query():
    engine = get_db_engine()
    seed_database(engine)
    executor = SQLExecutor(engine=engine)

    success, cols, rows, ms, err = executor.execute("SELECT product_name, price FROM products LIMIT 5;")

    assert success is True
    assert len(cols) == 2
    assert len(rows) > 0
    assert "product_name" in cols
    assert ms > 0.0
    assert err == ""


def test_executor_invalid_column_error():
    engine = get_db_engine()
    executor = SQLExecutor(engine=engine)

    success, cols, rows, ms, err = executor.execute("SELECT non_existent_column_123 FROM products;")

    assert success is False
    assert len(rows) == 0
    assert "no such column" in err.lower() or "column" in err.lower()
