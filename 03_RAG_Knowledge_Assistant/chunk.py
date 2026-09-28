import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


#Loads all pdf files from the data directory
all_documents = []
for filename in sorted(os.listdir(DATA_DIR)):
    if filename.endswith(".pdf"):
        filepath = os.path.join(DATA_DIR, filename)
        loader = PyPDFLoader(filepath)
        pages = loader.load()
        all_documents.extend(pages)

print(f"Total pages loaded: {len(all_documents)} from {len(os.listdir(DATA_DIR))} files}}")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE, 
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", " ", "", "."])

chunks = splitter.split_documents(all_documents)

print(f"Total chunks created: {len(chunks)} \n")

for i, chunk in enumerate(chunks[:3]):
    print(f"Chunk {i+1}:")
    print(f"Source: {chunk.metadata['source']}")
    print(f"Page : {chunk.metadata['page'] + 1}")
    print(f"Content: {chunk.page_content[:500]}...")  # Print first 500 characters of the content
    print("\n---\n")
