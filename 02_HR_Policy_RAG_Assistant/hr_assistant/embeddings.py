from langchain_community.embeddings import JinaEmbeddings
from hr_assistant import config

def get_embeddings_model():
    """Initialize and return the Jina embeddings model."""
    return JinaEmbeddings(model_name=config.EMBEDDING_MODEL_NAME) 