import logging
from typing import List, Dict, Any, Optional
from app.schemas.models import ChartConfig

logger = logging.getLogger("text_to_sql.visualizer")


class ChartGenerator:
    """
    Automated Data Visualization Engine.
    Analyzes column data types, row dimensions, and metrics to recommend optimal
    chart visualizers (Bar, Line, Pie, Metric Cards) and build Chart.js compatible specs.
    """

    @staticmethod
    def generate_chart_config(
        question: str,
        columns: List[str],
        data: List[Dict[str, Any]]
    ) -> Optional[ChartConfig]:
        """
        Determines the best chart type for query results and returns ChartConfig.
        """
        if not data or not columns:
            return None

        # 1. Single scalar result -> Metric KPI Card
        if len(data) == 1 and len(columns) == 1:
            val = list(data[0].values())[0]
            val_str = f"{val:,.2f}" if isinstance(val, (int, float)) else str(val)
            return ChartConfig(
                chart_type="metric",
                title=columns[0].replace("_", " ").title(),
                data=[val_str],
                chart_js_spec={"metric_label": columns[0], "metric_value": val_str}
            )

        # Classify columns into categorical (string/date) vs numerical
        numeric_cols = []
        string_cols = []
        date_cols = []

        first_row = data[0]
        for col in columns:
            val = first_row.get(col)
            if isinstance(val, (int, float)) and not (isinstance(val, bool)):
                numeric_cols.append(col)
            elif isinstance(val, str) and ("date" in col.lower() or "month" in col.lower() or "year" in col.lower() or "-" in val):
                date_cols.append(col)
            else:
                string_cols.append(col)

        # Primary label column (x-axis) and metric column (y-axis)
        label_col = (date_cols[0] if date_cols else (string_cols[0] if string_cols else columns[0]))
        metric_col = numeric_cols[0] if numeric_cols else None

        if not metric_col:
            # Fallback table view
            return ChartConfig(
                chart_type="table",
                title=f"Results for '{question}'",
                chart_js_spec={}
            )

        # Extract labels and values
        labels = [str(row.get(label_col, "")) for row in data]
        values = [float(row.get(metric_col, 0.0) or 0.0) for row in data]

        # Determine Chart Type
        chart_type = "bar"
        if date_cols or "trend" in question.lower() or "monthly" in question.lower():
            chart_type = "line"
        elif len(data) <= 6 and ("share" in question.lower() or "percentage" in question.lower() or "distribution" in question.lower()):
            chart_type = "pie"
        else:
            chart_type = "bar"

        # Construct Chart.js compatible configuration
        chart_js_spec = {
            "type": chart_type,
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": metric_col.replace("_", " ").title(),
                    "data": values,
                    "backgroundColor": [
                        "rgba(123, 44, 191, 0.7)",
                        "rgba(6, 182, 212, 0.7)",
                        "rgba(16, 185, 129, 0.7)",
                        "rgba(245, 158, 11, 0.7)",
                        "rgba(239, 68, 68, 0.7)",
                        "rgba(99, 102, 241, 0.7)",
                    ] if chart_type == "pie" else "rgba(123, 44, 191, 0.75)",
                    "borderColor": "rgba(123, 44, 191, 1)",
                    "borderWidth": 2,
                    "fill": chart_type == "line"
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {"display": chart_type == "pie"},
                    "title": {
                        "display": True,
                        "text": f"{metric_col.replace('_', ' ').title()} by {label_col.replace('_', ' ').title()}",
                        "color": "#f8fafc",
                        "font": {"size": 16, "family": "Inter"}
                    }
                }
            }
        }

        return ChartConfig(
            chart_type=chart_type,
            title=f"{metric_col.replace('_', ' ').title()} by {label_col.replace('_', ' ').title()}",
            x_axis=label_col,
            y_axis=metric_col,
            series=[metric_col],
            labels=labels,
            data=values,
            chart_js_spec=chart_js_spec
        )
