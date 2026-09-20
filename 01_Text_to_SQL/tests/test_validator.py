from app.core.validator import SQLGuardrailValidator


def test_valid_select_query():
    validator = SQLGuardrailValidator(max_row_limit=50)
    sql = "SELECT product_name, price FROM products WHERE stock_quantity = 0;"
    res = validator.validate(sql)

    assert res.is_valid is True
    assert "LIMIT 50" in res.sanitized_sql
    assert res.error_message is None


def test_reject_drop_table_mutation():
    validator = SQLGuardrailValidator()
    sql = "DROP TABLE products;"
    res = validator.validate(sql)

    assert res.is_valid is False
    assert "Forbidden mutation" in res.error_message or "Invalid statement type" in res.error_message


def test_reject_delete_statement():
    validator = SQLGuardrailValidator()
    sql = "DELETE FROM customers WHERE customer_id = 1;"
    res = validator.validate(sql)

    assert res.is_valid is False
    assert "Forbidden mutation" in res.error_message


def test_reject_multiple_statements_injection():
    validator = SQLGuardrailValidator()
    sql = "SELECT * FROM categories; DROP TABLE orders;"
    res = validator.validate(sql)

    assert res.is_valid is False
    assert "Multiple SQL statements" in res.error_message


def test_reject_system_catalog_access():
    validator = SQLGuardrailValidator()
    sql = "SELECT * FROM information_schema.tables;"
    res = validator.validate(sql)

    assert res.is_valid is False
    assert "system tables" in res.error_message.lower()


def test_limit_clause_capping():
    validator = SQLGuardrailValidator(max_row_limit=100)
    sql = "SELECT * FROM products LIMIT 5000;"
    res = validator.validate(sql)

    assert res.is_valid is True
    assert "LIMIT 100" in res.sanitized_sql
    assert res.applied_limit == 100
