import logging
from typing import List, Dict, Any
from sqlalchemy import inspect, text, Engine
from app.db.session import get_db_engine, get_db_type
from app.schemas.models import TableSchema, ColumnSchema, DatabaseSchemaResponse

logger = logging.getLogger("text_to_sql.schema")


class SchemaInspector:
    """
    Introspects the target SQL database dynamically to extract table metadata,
    column definitions, foreign key relationships, and representative sample rows.
    Provides schema context formatting for LLM prompt engineering.
    """

    def __init__(self, engine: Engine = None):
        self.engine = engine or get_db_engine()
        self.db_type = get_db_type()

    def get_full_schema(self) -> DatabaseSchemaResponse:
        """Retrieves structured schema definition for all tables in database."""
        inspector = inspect(self.engine)
        table_names = inspector.get_table_names()
        tables_metadata: List[TableSchema] = []

        with self.engine.connect() as conn:
            for table_name in table_names:
                # Get column details
                columns_raw = inspector.get_columns(table_name)
                pk_constraint = inspector.get_pk_constraint(table_name)
                pk_cols = pk_constraint.get("constrained_columns", [])
                fk_constraints = inspector.get_foreign_keys(table_name)

                # Map foreign keys by column name
                fk_map = {}
                for fk in fk_constraints:
                    referred_table = fk.get("referred_table")
                    referred_cols = fk.get("referred_columns", [])
                    constrained_cols = fk.get("constrained_columns", [])
                    if constrained_cols and referred_cols:
                        fk_map[constrained_cols[0]] = f"{referred_table}.{referred_cols[0]}"

                columns: List[ColumnSchema] = []
                for col in columns_raw:
                    c_name = col["name"]
                    c_type = str(col["type"])
                    is_pk = c_name in pk_cols
                    fk_ref = fk_map.get(c_name)

                    columns.append(ColumnSchema(
                        name=c_name,
                        type=c_type,
                        nullable=col.get("nullable", True),
                        primary_key=is_pk,
                        foreign_key=fk_ref,
                        description=f"{'Primary Key' if is_pk else ''} {'Foreign key referencing ' + fk_ref if fk_ref else ''}".strip()
                    ))

                # Get row count
                try:
                    count_res = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                except Exception:
                    count_res = 0

                # Get 3 sample rows
                sample_data: List[Dict[str, Any]] = []
                try:
                    sample_res = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 3")).mappings().all()
                    sample_data = [dict(row) for row in sample_res]
                except Exception as e:
                    logger.warning(f"Could not fetch sample rows for {table_name}: {e}")

                tables_metadata.append(TableSchema(
                    table_name=table_name,
                    row_count=count_res or 0,
                    columns=columns,
                    sample_data=sample_data
                ))

        return DatabaseSchemaResponse(
            database_type=self.db_type,
            total_tables=len(tables_metadata),
            tables=tables_metadata
        )

    def get_prompt_formatted_schema(self) -> str:
        """
        Formats the schema into a clean, LLM-optimized Markdown string.
        Includes table names, column names, data types, relationships, and sample values.
        """
        schema_data = self.get_full_schema()
        lines = [f"=== DATABASE SCHEMA ({schema_data.database_type.upper()}) ===", ""]

        for table in schema_data.tables:
            lines.append(f"Table: `{table.table_name}` (Total Rows: {table.row_count})")
            lines.append("Columns:")
            for col in table.columns:
                constraints = []
                if col.primary_key:
                    constraints.append("PRIMARY KEY")
                if col.foreign_key:
                    constraints.append(f"FOREIGN KEY -> {col.foreign_key}")
                
                c_str = f"  - `{col.name}` ({col.type})"
                if constraints:
                    c_str += f" [{', '.join(constraints)}]"
                lines.append(c_str)

            if table.sample_data:
                lines.append("Sample Rows:")
                for idx, row in enumerate(table.sample_data, start=1):
                    # Format as key=val summary
                    row_str = ", ".join([f"{k}={v}" for k, v in list(row.items())[:6]])
                    lines.append(f"  Row {idx}: {row_str}")
            lines.append("")

        return "\n".join(lines)
