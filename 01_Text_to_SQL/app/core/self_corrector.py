import logging
from typing import Dict, Any, Tuple, List
from app.config import settings
from app.core.validator import SQLGuardrailValidator
from app.core.executor import SQLExecutor
from app.llm.client import LLMClient

logger = logging.getLogger("text_to_sql.self_corrector")


class SQLSelfCorrector:
    """
    Manages the Agentic Self-Correction / Repair Loop when generated SQL fails AST validation
    or runtime PostgreSQL execution. Iteratively attempts repair up to MAX_RETRIES.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        validator: SQLGuardrailValidator,
        executor: SQLExecutor,
        max_retries: int = settings.MAX_SELF_CORRECTION_RETRIES
    ):
        self.llm_client = llm_client
        self.validator = validator
        self.executor = executor
        self.max_retries = max_retries

    def attempt_recovery(
        self,
        initial_failed_sql: str,
        initial_error: str,
        question: str,
        schema_context: str
    ) -> Tuple[bool, str, List[str], List[Dict[str, Any]], float, int, List[Dict[str, Any]], str]:
        """
        Runs iterative self-correction loop.
        Returns:
            - success (bool)
            - final_sanitized_sql (str)
            - columns (List[str])
            - rows (List[Dict[str, Any]])
            - total_correction_time_ms (float)
            - attempts_used (int)
            - correction_history (List[Dict[str, Any]])
            - final_error (str)
        """
        current_sql = initial_failed_sql
        current_error = initial_error
        correction_history: List[Dict[str, Any]] = []
        
        attempt = 0
        while attempt < self.max_retries:
            attempt += 1
            logger.info(f"Self-Correction Attempt {attempt}/{self.max_retries} for error: {current_error[:100]}...")

            # 1. Ask LLM to fix the query based on error traceback
            corrected_raw_sql = self.llm_client.self_correct_sql(
                failed_sql=current_sql,
                error_message=current_error,
                question=question,
                schema_context=schema_context
            )

            # 2. Validate newly corrected SQL
            val_res = self.validator.validate(corrected_raw_sql)
            if not val_res.is_valid:
                current_error = f"Validation Error: {val_res.error_message}"
                correction_history.append({
                    "attempt": attempt,
                    "attempted_sql": corrected_raw_sql,
                    "error": current_error,
                    "stage": "validation"
                })
                current_sql = corrected_raw_sql
                continue

            # 3. Try executing sanitized SQL
            exec_ok, cols, rows, exec_ms, exec_err = self.executor.execute(val_res.sanitized_sql)
            
            correction_history.append({
                "attempt": attempt,
                "attempted_sql": val_res.sanitized_sql,
                "stage": "execution",
                "success": exec_ok,
                "error": exec_err if not exec_ok else None,
                "row_count": len(rows) if exec_ok else 0
            })

            if exec_ok:
                logger.info(f"Self-Correction succeeded on attempt {attempt}!")
                return True, val_res.sanitized_sql, cols, rows, exec_ms, attempt, correction_history, ""

            # Update state for next iteration
            current_sql = val_res.sanitized_sql
            current_error = f"Database Execution Error: {exec_err}"

        logger.error(f"Self-Correction failed after {self.max_retries} attempts.")
        return False, current_sql, [], [], 0.0, attempt, correction_history, current_error
