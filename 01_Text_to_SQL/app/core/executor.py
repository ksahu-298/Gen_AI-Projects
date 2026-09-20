import time
import logging
from typing import Dict, Any, List, Tuple
from sqlalchemy import text, Engine
from app.db.session import get_db_engine

logger = logging.getLogger("text_to_sql.executor")


class SQLExecutor:
    """
    Executes read-only SQL queries against the database safely within a transaction boundary.
    Measures execution latency and converts DB result sets to standard Python dictionaries.
    """

    def __init__(self, engine: Engine = None):
        self.engine = engine or get_db_engine()

    def execute(self, sql_query: str) -> Tuple[bool, List[str], List[Dict[str, Any]], float, str]:
        """
        Executes a SQL query string.
        Returns:
            - success (bool)
            - columns (List[str])
            - rows (List[Dict[str, Any]])
            - execution_time_ms (float)
            - error_message (str)
        """
        start_time = time.perf_counter()
        
        try:
            with self.engine.connect() as conn:
                # Set statement timeout for safety if PostgreSQL
                if self.engine.dialect.name == "postgresql":
                    conn.execute(text("SET statement_timeout = 10000;"))

                result = conn.execute(text(sql_query))
                
                # Fetch columns
                columns = list(result.keys()) if result.returns_rows else []
                
                # Fetch rows
                rows_raw = result.mappings().all() if result.returns_rows else []
                
                # Convert decimal/datetime objects to JSON-serializable types
                rows: List[Dict[str, Any]] = []
                for row in rows_raw:
                    formatted_row = {}
                    for k, v in dict(row).items():
                        if hasattr(v, "isoformat"):
                            formatted_row[k] = v.isoformat()
                        elif hasattr(v, "__float__"):
                            formatted_row[k] = float(v)
                        else:
                            formatted_row[k] = v
                    rows.append(formatted_row)

                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.info(f"Successfully executed query in {elapsed_ms:.2f}ms ({len(rows)} rows returned)")
                
                return True, columns, rows, round(elapsed_ms, 2), ""

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            error_str = str(e)
            logger.error(f"SQL Execution Failed in {elapsed_ms:.2f}ms: {error_str}")
            return False, [], [], round(elapsed_ms, 2), error_str
