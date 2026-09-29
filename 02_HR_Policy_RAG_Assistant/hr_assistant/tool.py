from langchain.tools import tool
from hr_assistant.logger import get_logger

logger = get_logger(__name__)

def create_search_tool(retriever):
    """Create a LangChain tool for searching HR policy documents."""
    
    @tool
    def search_hr_policy(question: str) -> str:
        """Search the HR policy documents for information relevant to the query."""
        logger.info("search_hr_pilicy called with query : %s", question)       
        matching_chunks = retriever.invoke(question)
        logger.info("Found %d matching chunk(s)", len(matching_chunks))
        return "\n\n".join(chunk.page_content for chunk in matching_chunks)
    
    return search_hr_policy