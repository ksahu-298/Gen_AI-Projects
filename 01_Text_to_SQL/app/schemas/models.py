from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ColumnSchema(BaseModel):
    name: str
    type: str
    nullable: bool = True
    primary_key: bool = False
    foreign_key: Optional[str] = None
    description: Optional[str] = None


class TableSchema(BaseModel):
    table_name: str
    row_count: int
    columns: List[ColumnSchema]
    sample_data: List[Dict[str, Any]] = Field(default_factory=list)


class DatabaseSchemaResponse(BaseModel):
    database_type: str
    total_tables: int
    tables: List[TableSchema]


class ValidationResult(BaseModel):
    is_valid: bool
    sanitized_sql: str
    query_type: str = "SELECT"
    has_limit: bool = True
    applied_limit: Optional[int] = None
    error_message: Optional[str] = None
    security_warnings: List[str] = Field(default_factory=list)


class ChartConfig(BaseModel):
    chart_type: str  # bar, line, pie, metric, table
    title: str
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    series: List[str] = Field(default_factory=list)
    labels: List[str] = Field(default_factory=list)
    data: List[Any] = Field(default_factory=list)
    chart_js_spec: Dict[str, Any] = Field(default_factory=dict)


class QueryPipelineRequest(BaseModel):
    question: str = Field(..., json_schema_extra={"example": "Which top 5 customers spent the most money in 2024?"})
    allow_retry: bool = True
    custom_row_limit: Optional[int] = Field(default=50, ge=1, le=1000)


class PipelineStep(BaseModel):
    step_name: str
    duration_ms: float
    status: str  # success, error, retried
    details: Dict[str, Any] = Field(default_factory=dict)


class QueryPipelineResponse(BaseModel):
    question: str
    generated_sql: str
    validated_sql: str
    is_valid: bool
    execution_success: bool
    execution_time_ms: float
    total_latency_ms: float
    row_count: int
    columns: List[str] = Field(default_factory=list)
    data: List[Dict[str, Any]] = Field(default_factory=list)
    explanation: str
    chart_config: Optional[ChartConfig] = None
    self_correction_attempts: int = 0
    correction_history: List[Dict[str, Any]] = Field(default_factory=list)
    pipeline_steps: List[PipelineStep] = Field(default_factory=list)
    error: Optional[str] = None


class StandaloneValidationRequest(BaseModel):
    sql: str


class BenchmarkTestCase(BaseModel):
    id: str
    category: str  # Easy, Medium, Hard
    question: str
    expected_sql_pattern: Optional[str] = None
    min_expected_rows: Optional[int] = None


class EvaluationMetrics(BaseModel):
    total_cases: int
    successful_executions: int
    valid_sql_rate: float
    execution_accuracy: float
    self_correction_recovery_rate: float
    avg_latency_ms: float
    results_detail: List[Dict[str, Any]]
