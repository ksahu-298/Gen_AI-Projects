from fastapi import APIRouter
from app.core.validator import SQLGuardrailValidator
from app.schemas.models import StandaloneValidationRequest, ValidationResult

router = APIRouter()
validator = SQLGuardrailValidator()


@router.post("/validate-sql", response_model=ValidationResult, summary="Validate SQL Query Safety")
def validate_sql_query(request: StandaloneValidationRequest):
    """
    Performs standalone AST guardrail inspection on arbitrary SQL queries.
    Rejects DDL/DML mutations and enforces read-only LIMIT boundaries.
    """
    return validator.validate(request.sql)
