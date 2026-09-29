import os
from dotenv import load_dotenv

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

LANGSMITH_TRACING= os. getenv("LANGSMITH_TRACING", "false")
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT")

load_dotenv()


# Load environment variables from .env file
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

JINA_API_KEY = os.getenv("JINA_API_KEY")

# Data directory path and vector store path
DATA_FILE_PATH = str(PROJECT_ROOT / "data" / "hr_policy.txt")

VECTOR_STORE_PATH = str(PROJECT_ROOT / "data" / "faiss_index")

# Model names for LLM and embeddings
LLM_MODEL_NAME = "openai/gpt-oss-20b"

EMBEDDING_MODEL_NAME = "jina-embeddings-v2-base-en"

#Chunk size and overlap for text splitting
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

#Retriver Results
TOP_K_RESULTS = 3

#SYSTEM PROMPT for the RAG assistant
SYSTEM_PROMPT = """
You are an HR Policy Assistant. Your task is to provide accurate and concise information based on the HR policy documents. When answering questions, ensure that your responses are grounded in the provided documents. If the information is not available in the documents, respond with "I'm sorry, I don't have that information." Avoid making up answers or providing information not present in the documents.When referencing specific sections or clauses from the documents, please provide the exact text or a direct quote
"""

#Check API KEYS
def check_api_keys() -> None:
    """Check if the required API keys are set in the environment variables."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in the environment variables.")
    if not JINA_API_KEY:
        raise ValueError("JINA_API_KEY is not set in the environment variables.")
