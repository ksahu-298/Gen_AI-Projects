import os
import re
import logging
from typing import Optional
from app.config import settings
from app.llm.prompts import (
    SQL_GENERATION_SYSTEM_PROMPT,
    SQL_SELF_CORRECTION_SYSTEM_PROMPT,
    RESULT_EXPLANATION_PROMPT
)

logger = logging.getLogger("text_to_sql.llm")


class MockLLMEngine:
    """
    Deterministic rule-based mock engine used when no external API keys are provided.
    Guarantees out-of-the-box local execution and zero-key offline testing.
    """

    @staticmethod
    def generate_sql(question: str, schema_context: str) -> str:
        q_lower = question.lower()

        if "out of stock" in q_lower or "stock_quantity = 0" in q_lower or "out-of-stock" in q_lower:
            return """SELECT p.product_name, c.category_name, p.price, p.stock_quantity,
       SUM(oi.quantity * oi.unit_price) AS estimated_revenue
FROM products p
JOIN categories c ON p.category_id = c.category_id
LEFT JOIN order_items oi ON p.product_id = oi.product_id
WHERE p.stock_quantity = 0
GROUP BY p.product_id, p.product_name, c.category_name, p.price, p.stock_quantity
ORDER BY estimated_revenue DESC;"""

        elif "top" in q_lower and ("customer" in q_lower or "spent" in q_lower or "spending" in q_lower):
            return """SELECT c.customer_id, c.first_name, c.last_name, c.email, c.customer_segment,
       SUM(o.total_amount) AS total_spent, COUNT(o.order_id) AS order_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_status = 'Completed'
GROUP BY c.customer_id, c.first_name, c.last_name, c.email, c.customer_segment
ORDER BY total_spent DESC
LIMIT 5;"""

        elif "revenue by category" in q_lower or ("category" in q_lower and "sales" in q_lower):
            return """SELECT c.category_name, COUNT(DISTINCT p.product_id) as product_count,
       SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS total_revenue
FROM categories c
JOIN products p ON c.category_id = p.category_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status != 'Cancelled'
GROUP BY c.category_id, c.category_name
ORDER BY total_revenue DESC;"""

        elif "monthly" in q_lower or "trend" in q_lower or "date" in q_lower or "time" in q_lower:
            return """SELECT strftime('%Y-%m', order_date) as order_month,
       COUNT(order_id) as total_orders,
       SUM(total_amount) as monthly_revenue
FROM orders
WHERE order_status = 'Completed'
GROUP BY order_month
ORDER BY order_month ASC;"""

        elif "reorder" in q_lower or "low stock" in q_lower:
            return """SELECT p.product_name, c.category_name, p.stock_quantity, p.reorder_level
FROM products p
JOIN categories c ON p.category_id = c.category_id
WHERE p.stock_quantity <= p.reorder_level
ORDER BY p.stock_quantity ASC;"""

        else:
            return """SELECT p.product_name, c.category_name, p.price, p.stock_quantity
FROM products p
JOIN categories c ON p.category_id = c.category_id
ORDER BY p.price DESC
LIMIT 10;"""

    @staticmethod
    def fix_sql(failed_sql: str, error_message: str, question: str, schema_context: str) -> str:
        # Simple intelligent fix pattern
        if "no such column" in error_message.lower() or "column" in error_message.lower():
            # Replace common column errors if any
            fixed = re.sub(r'\bamount\b', 'total_amount', failed_sql, flags=re.IGNORECASE)
            fixed = re.sub(r'\bname\b', 'product_name', fixed, flags=re.IGNORECASE)
            return fixed
        elif "strftime" in error_message.lower() and "postgres" in schema_context.lower():
            return failed_sql.replace("strftime('%Y-%m', order_date)", "TO_CHAR(order_date, 'YYYY-MM')")
        return failed_sql


class LLMClient:
    """
    Unified LLM Client providing abstraction for Google Gemini, OpenAI, or Mock fallback.
    """

    def __init__(self, provider: Optional[str] = None):
        self.provider = (provider or settings.LLM_PROVIDER).lower()
        self.gemini_client = None
        self.openai_client = None

        if self.provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                from google import genai
                self.gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
                logger.info(f"Initialized Google Gemini Client ({settings.GEMINI_MODEL})")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Gemini client: {e}. Falling back to mock engine.")
                self.provider = "mock"

        elif self.provider == "openai" and settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info(f"Initialized OpenAI Client ({settings.OPENAI_MODEL})")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}. Falling back to mock engine.")
                self.provider = "mock"
        else:
            logger.info("Using MockLLMEngine for SQL generation (Zero API Key Mode).")
            self.provider = "mock"

    def generate_sql(self, question: str, schema_context: str) -> str:
        """Generates SQL query from natural language question and schema context."""
        prompt = SQL_GENERATION_SYSTEM_PROMPT.format(
            schema_context=schema_context,
            question=question
        )

        if self.provider == "gemini" and self.gemini_client:
            try:
                response = self.gemini_client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=prompt
                )
                return response.text or ""
            except Exception as e:
                logger.error(f"Gemini API call failed: {e}. Using mock engine fallback.")
                return MockLLMEngine.generate_sql(question, schema_context)

        elif self.provider == "openai" and self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                logger.error(f"OpenAI API call failed: {e}. Using mock engine fallback.")
                return MockLLMEngine.generate_sql(question, schema_context)

        else:
            return MockLLMEngine.generate_sql(question, schema_context)

    def self_correct_sql(self, failed_sql: str, error_message: str, question: str, schema_context: str) -> str:
        """Fixes invalid SQL query using error traceback and schema context."""
        prompt = SQL_SELF_CORRECTION_SYSTEM_PROMPT.format(
            schema_context=schema_context,
            failed_sql=failed_sql,
            error_message=error_message,
            question=question
        )

        if self.provider == "gemini" and self.gemini_client:
            try:
                response = self.gemini_client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=prompt
                )
                return response.text or ""
            except Exception as e:
                logger.error(f"Gemini Self-Correction failed: {e}")
                return MockLLMEngine.fix_sql(failed_sql, error_message, question, schema_context)

        elif self.provider == "openai" and self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                logger.error(f"OpenAI Self-Correction failed: {e}")
                return MockLLMEngine.fix_sql(failed_sql, error_message, question, schema_context)

        else:
            return MockLLMEngine.fix_sql(failed_sql, error_message, question, schema_context)

    def generate_explanation(self, question: str, sql_query: str, row_count: int, data_sample: str) -> str:
        """Generates plain-English executive explanation of results."""
        prompt = RESULT_EXPLANATION_PROMPT.format(
            question=question,
            sql_query=sql_query,
            row_count=row_count,
            data_sample=data_sample
        )

        if self.provider == "gemini" and self.gemini_client:
            try:
                response = self.gemini_client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=prompt
                )
                return response.text.strip()
            except Exception:
                pass

        elif self.provider == "openai" and self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content.strip()
            except Exception:
                pass

        # Fallback explanation generator
        if row_count == 0:
            return f"The query executed successfully but returned 0 rows for question: '{question}'."
        return f"Successfully retrieved {row_count} records answering: '{question}'. Key data columns include relevant business metrics analyzed according to the database schema."
