from fastapi import APIRouter, HTTPException
from app.core.pipeline import TextToSQLPipeline
from app.schemas.models import QueryPipelineRequest, QueryPipelineResponse

router = APIRouter()
pipeline = TextToSQLPipeline()


@router.post("/query", response_model=QueryPipelineResponse, summary="Execute Text-to-SQL Pipeline")
def process_natural_language_query(request: QueryPipelineRequest):
    """
    Translates a natural language question into a safe SQL query, validates it via AST guardrails,
    executes it against PostgreSQL/SQLite, auto-corrects on failure, and returns chart/explanation metadata.
    """
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        response = pipeline.run(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
