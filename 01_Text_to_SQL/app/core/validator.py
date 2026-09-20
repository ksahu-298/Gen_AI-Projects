import re
import logging
from typing import Optional, List, Tuple
import sqlglot
from sqlglot import exp
from app.config import settings
from app.schemas.models import ValidationResult

logger = logging.getLogger("text_to_sql.validator")

# Forbidden SQL keywords / expression types
MUTATION_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE",
    "GRANT", "REVOKE", "COPY", "EXEC", "EXECUTE", "VACUUM", "REINDEX",
    "ATTACH", "DETACH", "MERGE", "UPSERT", "PRAGMA", "SHUTDOWN"
}

FORBIDDEN_TABLE_PATTERNS = [
    r"\bpg_\w+", r"\binformation_schema\b", r"\bsqlite_\w+", r"\bsys\.\w+"
]


class SQLGuardrailValidator:
    """
    AST-based guardrail validator for LLM-generated SQL queries.
    Ensures safe, read-only analytical execution and enforces query bounds.
    """

    def __init__(
        self,
        max_row_limit: int = settings.MAX_QUERY_ROW_LIMIT,
        dialect: str = "postgres"
    ):
        self.max_row_limit = max_row_limit
        self.dialect = dialect

    def validate(self, raw_sql: str) -> ValidationResult:
        """
        Validates raw SQL query using AST parsing and rule enforcement.
        Returns ValidationResult with safety evaluation and sanitized SQL.
        """
        if not raw_sql or not raw_sql.strip():
            return ValidationResult(
                is_valid=False,
                sanitized_sql="",
                error_message="Empty SQL query provided."
            )

        # 1. Clean Markdown formatting & whitespace
        clean_sql = self._strip_markdown_code_blocks(raw_sql)
        warnings: List[str] = []

        # 2. Check for multiple statements (semicolon injection)
        statements = [s.strip() for s in clean_sql.split(";") if s.strip()]
        if len(statements) > 1:
            return ValidationResult(
                is_valid=False,
                sanitized_sql=clean_sql,
                error_message="Multiple SQL statements detected. Only a single SELECT query is permitted for safety."
            )

        single_query = statements[0]

        # 3. Regex Boundary Check for forbidden mutation keywords
        upper_query = single_query.upper()
        for kw in MUTATION_KEYWORDS:
            if re.search(r'\b' + kw + r'\b', upper_query):
                return ValidationResult(
                    is_valid=False,
                    sanitized_sql=single_query,
                    error_message=f"Forbidden mutation or state-changing keyword detected: '{kw}'. Only SELECT queries are permitted."
                )

        # 4. Check forbidden system table access
        for pattern in FORBIDDEN_TABLE_PATTERNS:
            if re.search(pattern, single_query, re.IGNORECASE):
                return ValidationResult(
                    is_valid=False,
                    sanitized_sql=single_query,
                    error_message="Access to system tables or metadata catalogs is prohibited."
                )

        # 5. AST Parsing with sqlglot
        try:
            parsed_expressions = sqlglot.parse(single_query, read=self.dialect)
            if not parsed_expressions or parsed_expressions[0] is None:
                # Fallback dialect check
                parsed_expressions = sqlglot.parse(single_query)
            
            ast = parsed_expressions[0]

            # Verify statement type is SELECT or CTE
            if not (isinstance(ast, exp.Select) or isinstance(ast, exp.Union)):
                return ValidationResult(
                    is_valid=False,
                    sanitized_sql=single_query,
                    error_message=f"Invalid statement type: '{ast.key.upper()}'. Query must be a SELECT query."
                )

            # Ensure NO AST mutation sub-expressions exist
            for node in ast.walk():
                if isinstance(node, (exp.Insert, exp.Update, exp.Delete, exp.Create, exp.Drop, exp.Alter)):
                    return ValidationResult(
                        is_valid=False,
                        sanitized_sql=single_query,
                        error_message="AST contains forbidden mutation node."
                    )

            # 6. Check and Enforce LIMIT Clause
            has_limit = False
            applied_limit = None
            
            limit_expression = ast.find(exp.Limit)
            if limit_expression:
                has_limit = True
                try:
                    val = int(limit_expression.expression.this)
                    if val > self.max_row_limit:
                        # Cap limit to max allowed limit
                        limit_expression.expression.replace(sqlglot.parse_one(str(self.max_row_limit)))
                        applied_limit = self.max_row_limit
                        warnings.append(f"Query limit {val} exceeded maximum threshold. Capped to {self.max_row_limit}.")
                    else:
                        applied_limit = val
                except Exception:
                    applied_limit = self.max_row_limit
            else:
                # Auto-append LIMIT clause
                ast = ast.limit(self.max_row_limit)
                has_limit = True
                applied_limit = self.max_row_limit
                warnings.append(f"No LIMIT specified. Automatically appended 'LIMIT {self.max_row_limit}' for safety.")

            sanitized_sql = ast.sql(dialect=self.dialect, pretty=True)

            return ValidationResult(
                is_valid=True,
                sanitized_sql=sanitized_sql,
                query_type="SELECT",
                has_limit=has_limit,
                applied_limit=applied_limit,
                security_warnings=warnings
            )

        except sqlglot.errors.ParseError as pe:
            logger.warning(f"SQLGlot AST parse warning: {pe}. Falling back to basic regex validation.")
            # If AST parsing fails due to dialect features, allow if basic regex checks pass
            if not upper_query.startswith("SELECT") and not upper_query.startswith("WITH"):
                return ValidationResult(
                    is_valid=False,
                    sanitized_sql=single_query,
                    error_message="Query does not start with SELECT or WITH statement."
                )
            
            # Append LIMIT if missing
            sanitized_sql = single_query
            if "LIMIT" not in upper_query:
                sanitized_sql = f"{single_query}\nLIMIT {self.max_row_limit}"
                warnings.append(f"Automatically appended 'LIMIT {self.max_row_limit}'.")

            return ValidationResult(
                is_valid=True,
                sanitized_sql=sanitized_sql,
                query_type="SELECT",
                has_limit=True,
                applied_limit=self.max_row_limit,
                security_warnings=warnings
            )

    @staticmethod
    def _strip_markdown_code_blocks(text: str) -> str:
        """Strips ```sql ... ``` wrappers from raw LLM output."""
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return text
