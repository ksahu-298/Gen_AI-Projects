from langchain_groq import ChatGroq
from hr_assistant import config
from hr_assistant.logger import get_logger

logger = get_logger(__name__)

def get_llm():
    """Initialize and return the ChatGroq LLM model."""
    logger.info("Initializing LLM '%s'", config.LLM_MODEL_NAME)
    return ChatGroq(model_name=config.LLM_MODEL_NAME, temperature = 0) 