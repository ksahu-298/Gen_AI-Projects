import os
import json
import logging
from fastapi import APIRouter
from app.core.pipeline import TextToSQLPipeline
from app.schemas.models import QueryPipelineRequest, EvaluationMetrics

logger = logging.getLogger("text_to_sql.api.eval")
router = APIRouter()
pipeline = TextToSQLPipeline()


@router.get("/eval", response_model=EvaluationMetrics, summary="Run Evaluation Benchmark Suite")
def run_evaluation_benchmark():
    """
    Executes the golden benchmark evaluation suite against the system,
    measuring SQL syntax validity, execution accuracy, self-correction rate, and average latency.
    """
    dataset_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "eval", "dataset.json")
    
    if not os.path.exists(dataset_path):
        return EvaluationMetrics(
            total_cases=0,
            successful_executions=0,
            valid_sql_rate=0.0,
            execution_accuracy=0.0,
            self_correction_recovery_rate=0.0,
            avg_latency_ms=0.0,
            results_detail=[]
        )

    with open(dataset_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    results_detail = []
    valid_count = 0
    success_count = 0
    self_corrected_count = 0
    total_latency = 0.0

    for test_case in test_cases:
        req = QueryPipelineRequest(question=test_case["question"], allow_retry=True)
        res = pipeline.run(req)

        if res.is_valid:
            valid_count += 1
        if res.execution_success:
            success_count += 1
        if res.self_correction_attempts > 0 and res.execution_success:
            self_corrected_count += 1
        
        total_latency += res.total_latency_ms

        results_detail.append({
            "id": test_case["id"],
            "category": test_case["category"],
            "question": test_case["question"],
            "is_valid": res.is_valid,
            "execution_success": res.execution_success,
            "row_count": res.row_count,
            "self_correction_attempts": res.self_correction_attempts,
            "total_latency_ms": res.total_latency_ms,
            "sql": res.validated_sql
        })

    total = len(test_cases)
    return EvaluationMetrics(
        total_cases=total,
        successful_executions=success_count,
        valid_sql_rate=round((valid_count / total) * 100, 2) if total > 0 else 0.0,
        execution_accuracy=round((success_count / total) * 100, 2) if total > 0 else 0.0,
        self_correction_recovery_rate=round((self_corrected_count / max(1, total - (success_count - self_corrected_count))) * 100, 2),
        avg_latency_ms=round(total_latency / total, 2) if total > 0 else 0.0,
        results_detail=results_detail
    )
