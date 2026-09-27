from langchain_groq import ChatGroq
from hr_assistant import config

def get_llm():
    """Initialize and return the ChatGroq LLM model."""
    return ChatGroq(model_name=config.LLM_MODEL_NAME, temperature = 0) 