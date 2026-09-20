import time
import logging
from typing import Optional
from app.db.schema_inspector import SchemaInspector
from app.core.validator import SQLGuardrailValidator
from app.core.executor import SQLExecutor
from app.core.self_corrector import SQLSelfCorrector
from app.core.visualizer import ChartGenerator
from app.core.explainer import ResultExplainer
from app.llm.client import LLMClient
from app.schemas.models import (
    QueryPipelineRequest,
    QueryPipelineResponse,
    PipelineStep
)

logger = logging.getLogger("text_to_sql.pipeline")


class TextToSQLPipeline:
    """
    Production-grade Text-to-SQL Pipeline.
    Orchestrates Question -> Schema Context -> LLM SQL Gen -> AST Guardrails ->
    PostgreSQL Execution -> Self-Correction Loop -> Visualization -> Executive Summary.
    """

    def __init__(
        self,
        schema_inspector: Optional[SchemaInspector] = None,
        validator: Optional[SQLGuardrailValidator] = None,
        executor: Optional[SQLExecutor] = None,
        llm_client: Optional[LLMClient] = None
    ):
        self.schema_inspector = schema_inspector or SchemaInspector()
        self.validator = validator or SQLGuardrailValidator()
        self.executor = executor or SQLExecutor()
        self.llm_client = llm_client or LLMClient()
        self.self_corrector = SQLSelfCorrector(
            llm_client=self.llm_client,
            validator=self.validator,
            executor=self.executor
        )
        self.explainer = ResultExplainer(llm_client=self.llm_client)

    def run(self, request: QueryPipelineRequest) -> QueryPipelineResponse:
        """Executes full pipeline for a given user question."""
        pipeline_start = time.perf_counter()
        pipeline_steps = []

        # Step 1: Retrieve Database Schema Context
        step_start = time.perf_counter()
        schema_context = self.schema_inspector.get_prompt_formatted_schema()
        schema_ms = (time.perf_counter() - step_start) * 1000
        pipeline_steps.append(PipelineStep(
            step_name="Retrieve Schema Context",
            duration_ms=round(schema_ms, 2),
            status="success"
        ))

        # Step 2: LLM SQL Generation
        step_start = time.perf_counter()
        raw_sql = self.llm_client.generate_sql(
            question=request.question,
            schema_context=schema_context
        )
        gen_ms = (time.perf_counter() - step_start) * 1000
        pipeline_steps.append(PipelineStep(
            step_name="LLM SQL Generation",
            duration_ms=round(gen_ms, 2),
            status="success",
            details={"raw_sql": raw_sql}
        ))

        # Step 3: AST Guardrail Validation
        step_start = time.perf_counter()
        val_res = self.validator.validate(raw_sql)
        val_ms = (time.perf_counter() - step_start) * 1000
        pipeline_steps.append(PipelineStep(
            step_name="AST Guardrail Validation",
            duration_ms=round(val_ms, 2),
            status="success" if val_res.is_valid else "error",
            details={"is_valid": val_res.is_valid, "warnings": val_res.security_warnings}
        ))

        # Check validation failure
        if not val_res.is_valid:
            if request.allow_retry:
                # Trigger Self-Correction
                logger.info("SQL Validation failed. Entering Agentic Self-Correction...")
                sc_ok, final_sql, cols, rows, sc_exec_ms, retries, history, err = self.self_corrector.attempt_recovery(
                    initial_failed_sql=raw_sql,
                    initial_error=val_res.error_message or "Invalid AST structure",
                    question=request.question,
                    schema_context=schema_context
                )
                total_ms = (time.perf_counter() - pipeline_start) * 1000

                if sc_ok:
                    chart_cfg = ChartGenerator.generate_chart_config(request.question, cols, rows)
                    explanation = self.explainer.explain(request.question, final_sql, cols, rows)
                    return QueryPipelineResponse(
                        question=request.question,
                        generated_sql=raw_sql,
                        validated_sql=final_sql,
                        is_valid=True,
                        execution_success=True,
                        execution_time_ms=sc_exec_ms,
                        total_latency_ms=round(total_ms, 2),
                        row_count=len(rows),
                        columns=cols,
                        data=rows,
                        explanation=explanation,
                        chart_config=chart_cfg,
                        self_correction_attempts=retries,
                        correction_history=history,
                        pipeline_steps=pipeline_steps
                    )
            
            # Unrecoverable validation failure
            total_ms = (time.perf_counter() - pipeline_start) * 1000
            return QueryPipelineResponse(
                question=request.question,
                generated_sql=raw_sql,
                validated_sql=val_res.sanitized_sql,
                is_valid=False,
                execution_success=False,
                execution_time_ms=0.0,
                total_latency_ms=round(total_ms, 2),
                row_count=0,
                explanation=f"Query rejected by security guardrails: {val_res.error_message}",
                pipeline_steps=pipeline_steps,
                error=val_res.error_message
            )

        # Step 4: Execute Validated Query
        step_start = time.perf_counter()
        exec_ok, cols, rows, exec_ms, exec_err = self.executor.execute(val_res.sanitized_sql)
        pipeline_steps.append(PipelineStep(
            step_name="PostgreSQL Execution",
            duration_ms=exec_ms,
            status="success" if exec_ok else "error",
            details={"row_count": len(rows), "error": exec_err if not exec_ok else None}
        ))

        # Check execution failure -> Self Correction Loop
        if not exec_ok:
            if request.allow_retry:
                logger.info(f"Execution failed ({exec_err}). Entering Agentic Self-Correction...")
                sc_ok, final_sql, cols, rows, sc_exec_ms, retries, history, err = self.self_corrector.attempt_recovery(
                    initial_failed_sql=val_res.sanitized_sql,
                    initial_error=exec_err,
                    question=request.question,
                    schema_context=schema_context
                )
                total_ms = (time.perf_counter() - pipeline_start) * 1000

                if sc_ok:
                    chart_cfg = ChartGenerator.generate_chart_config(request.question, cols, rows)
                    explanation = self.explainer.explain(request.question, final_sql, cols, rows)
                    return QueryPipelineResponse(
                        question=request.question,
                        generated_sql=raw_sql,
                        validated_sql=final_sql,
                        is_valid=True,
                        execution_success=True,
                        execution_time_ms=sc_exec_ms,
                        total_latency_ms=round(total_ms, 2),
                        row_count=len(rows),
                        columns=cols,
                        data=rows,
                        explanation=explanation,
                        chart_config=chart_cfg,
                        self_correction_attempts=retries,
                        correction_history=history,
                        pipeline_steps=pipeline_steps
                    )

            total_ms = (time.perf_counter() - pipeline_start) * 1000
            return QueryPipelineResponse(
                question=request.question,
                generated_sql=raw_sql,
                validated_sql=val_res.sanitized_sql,
                is_valid=True,
                execution_success=False,
                execution_time_ms=exec_ms,
                total_latency_ms=round(total_ms, 2),
                row_count=0,
                explanation=f"Query execution failed: {exec_err}",
                pipeline_steps=pipeline_steps,
                error=exec_err
            )

        # Step 5: Generate Chart Visualization & Explanation
        step_start = time.perf_counter()
        chart_cfg = ChartGenerator.generate_chart_config(request.question, cols, rows)
        explanation = self.explainer.explain(request.question, val_res.sanitized_sql, cols, rows)
        viz_ms = (time.perf_counter() - step_start) * 1000

        pipeline_steps.append(PipelineStep(
            step_name="Visualization & Explanation",
            duration_ms=round(viz_ms, 2),
            status="success"
        ))

        total_ms = (time.perf_counter() - pipeline_start) * 1000

        return QueryPipelineResponse(
            question=request.question,
            generated_sql=raw_sql,
            validated_sql=val_res.sanitized_sql,
            is_valid=True,
            execution_success=True,
            execution_time_ms=exec_ms,
            total_latency_ms=round(total_ms, 2),
            row_count=len(rows),
            columns=cols,
            data=rows,
            explanation=explanation,
            chart_config=chart_cfg,
            self_correction_attempts=0,
            pipeline_steps=pipeline_steps
        )
