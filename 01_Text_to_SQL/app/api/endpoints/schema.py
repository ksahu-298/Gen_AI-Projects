from fastapi import APIRouter
from app.db.schema_inspector import SchemaInspector
from app.schemas.models import DatabaseSchemaResponse

router = APIRouter()
inspector = SchemaInspector()


@router.get("/schema", response_model=DatabaseSchemaResponse, summary="Inspect Database Schema")
def get_database_schema():
    """
    Returns full metadata for all tables, columns, foreign keys, row counts, and sample data.
    """
    return inspector.get_full_schema()
