from app.core.pipeline import TextToSQLPipeline
from app.schemas.models import QueryPipelineRequest


def test_pipeline_out_of_stock_query():
    pipeline = TextToSQLPipeline()
    req = QueryPipelineRequest(
        question="Which out-of-stock products have the highest estimated revenue?",
        allow_retry=True
    )
    res = pipeline.run(req)

    assert res.is_valid is True
    assert res.execution_success is True
    assert res.row_count >= 0
    assert res.validated_sql is not None
    assert "stock_quantity" in res.validated_sql.lower()
    assert res.total_latency_ms > 0
    assert res.explanation is not None


def test_pipeline_top_customers_query():
    pipeline = TextToSQLPipeline()
    req = QueryPipelineRequest(
        question="Who are the top 5 customers by total spending?",
        allow_retry=True
    )
    res = pipeline.run(req)

    assert res.is_valid is True
    assert res.execution_success is True
    assert len(res.data) <= 5
