from langchain.tools import tool

def create_search_tool(retriever):
    """Create a LangChain tool for searching HR policy documents."""
    
    @tool
    def search_hr_policy(question: str) -> str:
        """Search the HR policy documents for information relevant to the query."""
        matching_chunks = retriever.invoke(question)
        return "\n\n".join(chunk.page_content for chunk in matching_chunks)
    
    return search_hr_policy