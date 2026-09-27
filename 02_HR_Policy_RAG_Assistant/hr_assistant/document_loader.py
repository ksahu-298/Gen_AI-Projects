from langchain_community.document_loaders import TextLoader
from hr_assistant import config

def load_document(file_path: str = config.DATA_FILE_PATH):
    """Load the document from the specified file path."""
    loader = TextLoader(file_path, encoding="utf-8")
    return loader.load()