import logging
from typing import List, Dict, Any
from app.llm.client import LLMClient

logger = logging.getLogger("text_to_sql.explainer")


class ResultExplainer:
    """
    Generates plain-English summaries and executive findings from database query results.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def explain(
        self,
        question: str,
        sql_query: str,
        columns: List[str],
        data: List[Dict[str, Any]]
    ) -> str:
        """
        Generates executive summary of database query results.
        """
        row_count = len(data)

        if row_count == 0:
            return f"No matching records were found in the database for the request: '{question}'."

        # Format top 3 sample rows as readable context string
        sample_str = ""
        for idx, row in enumerate(data[:3], start=1):
            sample_str += f"Row {idx}: " + ", ".join([f"{k}={v}" for k, v in row.items()]) + "\n"

        return self.llm_client.generate_explanation(
            question=question,
            sql_query=sql_query,
            row_count=row_count,
            data_sample=sample_str
        )
