import os, time
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# os.environ["NVIDIA_API_KEY"] = os.getenv("NVIDIA_API_KEY")
# os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
for key in ("NVIDIA_API_KEY", "PINECONE_API_KEY"):
    if not os.getenv(key):
        raise ValueError(f"{key} is missing; check your .env file")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

INDEX_NAME = "knowledge-assistant"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

all_documents = []
for filename in sorted(os.listdir(DATA_DIR)):
    if filename.endswith(".pdf"):
        filepath = os.path.join(DATA_DIR, filename)
        loader = PyPDFLoader(filepath)
        pages = loader.load()
        all_documents.extend(pages)

print(f"Total pages loaded: {len(all_documents)} from {len(os.listdir(DATA_DIR))} files")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE, 
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", " ", ".", ""])

chunks = splitter.split_documents(all_documents)
print(f"Total chunks created: {len(chunks)} \n")

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

existing_indexes = [i.name for i in pc.list_indexes()]

if INDEX_NAME in existing_indexes:
    pc.delete_index(INDEX_NAME)
    print(f"Deleted existing index: {INDEX_NAME}")
    time.sleep(5)  # Wait for a few seconds to ensure the index is deleted

pc.create_index(
    name=INDEX_NAME,
    dimension=2048,  # Dimension for NVIDIA embeddings
    metric="cosine",
    spec = ServerlessSpec(cloud="aws", region="us-east-1"),
)

print(f"Created new index: {INDEX_NAME}")

while not pc.describe_index(INDEX_NAME).status["ready"]:
    time.sleep(1)

print(f"Index {INDEX_NAME} is ready for use.")

print("Initializing NVIDIA embeddings...")

embeddings = NVIDIAEmbeddings(
    model="nvidia/nemotron-3-embed-1b",
    truncate="END"
)

vector_store = PineconeVectorStore.from_documents(
    documents=chunks,
    embedding=embeddings,
    index_name=INDEX_NAME

)

print(f"Successfully stored {len(chunks)} chunks in Pinecone index: {INDEX_NAME}")  

















