import os
from langchain_community.vectorstores import FAISS
from hr_assistant import config
from hr_assistant.embeddings import get_embeddings_model


# build_vector_store 
def build_vector_store(chunks):
    """Embed every chunk and upload it into a Qdrant Cloud collection."""
    embeddings_model = get_embeddings_model()
    return FAISS.from_documents(chunks, embeddings_model)

#save_vector_store
def save_vector_store(vector_store, path: str = config.VECTOR_STORE_PATH) -> None:
    """Save the vector store to the specified path."""
    vector_store.save_local(path)

#load_vector_store
def load_vector_store(path: str = config.VECTOR_STORE_PATH):
    """Load the vector store from the specified path."""
    embeddings_model = get_embeddings_model()
    return FAISS.load_local(path, embeddings_model, allow_dangerous_deserialization=True)

#check_vector_store_exists
def check_vector_store_exists(path: str = config.VECTOR_STORE_PATH) -> bool:
    """Check if the vector store exists at the specified path."""
    return os.path.exists(os.path.join(path, "index.faiss"))

#get retriever
def get_retriever(vector_store, k: int = config.TOP_K_RESULTS):
    """Get a retriever from the vector store."""  
    return vector_store.as_retriever(search_kwargs={"k": k})  

 