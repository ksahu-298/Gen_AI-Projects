import os
from langchain_community.document_loaders import PyPDFLoader


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

all_documents = []
for filename in sorted(os.listdir(DATA_DIR)):
    if filename.endswith(".pdf"):
        filepath = os.path.join(DATA_DIR, filename)
        loader = PyPDFLoader(filepath)
        pages = loader.load()
        all_documents.extend(pages)
        print(f"Loaded : {len(pages)} pages from {filename}")

print(f"Total pages loaded: {len(all_documents)}")

print("\n ---- Preview of the first 1 pages ---- \n")
doc = all_documents[0]
print(f"Source: {doc.metadata['source']}")
print(f"Page : {doc.metadata['page'] + 1}")
print(f"Content: {doc.page_content[:500]}...")  # Print first 500 characters of the content

    