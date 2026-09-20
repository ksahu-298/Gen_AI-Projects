import sys
import os
import json
import time

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.pipeline import TextToSQLPipeline
from app.schemas.models import QueryPipelineRequest


def run_standalone_evaluation():
    print("==========================================================================")
    print("        TALK TO YOUR DATA - TEXT-TO-SQL BENCHMARK EVALUATOR               ")
    print("==========================================================================")

    dataset_path = os.path.join(os.path.dirname(__file__), "dataset.json")
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset file not found at {dataset_path}")
        sys.exit(1)

    with open(dataset_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    pipeline = TextToSQLPipeline()

    valid_count = 0
    success_count = 0
    self_corrected_count = 0
    total_latency_ms = 0.0

    print(f"Running evaluation benchmark on {len(test_cases)} golden test cases...\n")

    for idx, tc in enumerate(test_cases, start=1):
        question = tc["question"]
        category = tc["category"]

        req = QueryPipelineRequest(question=question, allow_retry=True)
        res = pipeline.run(req)

        is_valid = res.is_valid
        is_success = res.execution_success
        sc_attempts = res.self_correction_attempts
        lat = res.total_latency_ms

        if is_valid:
            valid_count += 1
        if is_success:
            success_count += 1
        if sc_attempts > 0 and is_success:
            self_corrected_count += 1

        total_latency_ms += lat

        status_str = "SUCCESS" if is_success else "FAILED"
        print(f"[{idx:02d}/{len(test_cases):02d}] {status_str} | {category:20s} | Latency: {lat:6.1f}ms | Q: '{question}'")
        if not is_success:
            print(f"     -> Error: {res.error}")

    total = len(test_cases)
    acc = (success_count / total) * 100 if total > 0 else 0.0
    val_rate = (valid_count / total) * 100 if total > 0 else 0.0
    avg_lat = total_latency_ms / total if total > 0 else 0.0

    print("\n==========================================================================")
    print("                           EVALUATION REPORT MATRIX                       ")
    print("==========================================================================")
    print(f"Total Benchmark Cases Evaluated : {total}")
    print(f"Syntactic Valid SQL Rate        : {val_rate:.2f}%")
    print(f"PostgreSQL Execution Accuracy   : {acc:.2f}%")
    print(f"Self-Correction Recovery Rate   : {self_corrected_count} test cases repaired")
    print(f"Average Pipeline Latency        : {avg_lat:.2f} ms")
    print("==========================================================================\n")


if __name__ == "__main__":
    run_standalone_evaluation()
