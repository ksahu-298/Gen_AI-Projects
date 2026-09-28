import os
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

nvidia_api_key = os.getenv("NVIDIA_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")

if not nvidia_api_key or not pinecone_api_key:
    raise ValueError("Check that NVIDIA_API_KEY and PINECONE_API_KEY are set in .env")

INDEX_NAME = "knowledge-assistant"

embeddings = NVIDIAEmbeddings(
    model="nvidia/nemotron-3-embed-1b",
    truncate="END"
)

vector_store = PineconeVectorStore(
    embedding=embeddings,
    index_name=INDEX_NAME
)

print(f'Connected to Pinecone Index {INDEX_NAME}')


question = "What is the employee leave policy?"
print(f'Question: {question}\n')


result = vector_store.similarity_search(question, k=3)


print(f'Top 3 Result: \n')

for i, doc in enumerate(result,1):
    source = os.path.basename(doc.metadata['source'])
    page = doc.metadata["page"] + 1
    print(f"---Result {i} | {source}, Page {page} ---")
    print(doc.page_content[:250] + "...\n")