# Company Docs AI Chatbot (End-to-End RAG Project)

An AI chatbot that answers questions from company PDFs (HR policy, IT security, product guide) and **cites the source file and page for every answer**. When the answer isn't in the documents, it replies "I don't know" instead of guessing.

**Live demo:** [rag-knowledge-assist.streamlit.app](https://rag-knowledge-assist.streamlit.app/)

**Stack:** LangChain, NVIDIA AI Endpoints (`nvidia/nemotron-3-embed-1b`), Pinecone, Groq, Streamlit

---

## What It Does

- Answers questions about the HR policy, IT security policy and product guide in plain English
- Cites the file name and page number behind every fact
- Says "I don't know" when the documents don't contain the answer
- Runs as an interactive Streamlit dashboard, deployed on Streamlit Community Cloud

## How It Works

1. **Load** — company PDFs (HR policy, IT security, product guide) are loaded with LangChain.
2. **Split** — each document is cut into overlapping chunks, which keeps context intact and improves retrieval.
3. **Embed** — chunks are turned into vectors with free NVIDIA embeddings (`nvidia/nemotron-3-embed-1b`).
4. **Store and search** — vectors live in Pinecone, a serverless vector database, and the most relevant chunks are retrieved for each question.
5. **Answer** — a Groq-hosted LLM writes the answer from the retrieved chunks only, citing the file and page for every fact.
6. **Fallback** — if the retrieved text doesn't contain the answer, the bot replies "I don't know".

## Tech Stack

All on free tiers.

| Layer | Technology |
|---|---|
| Orchestration | LangChain |
| Embeddings | NVIDIA AI Endpoints (`nvidia/nemotron-3-embed-1b`) |
| Vector database | Pinecone (serverless) |
| LLM | Groq (`qwen/qwen3.8-27b`) |
| UI and deployment | Streamlit, Streamlit Community Cloud |
| Language | Python |

## Project Files

| File | Purpose |
|---|---|
| `create_sample_docs.py` | Generates the sample company PDFs |
| `step3_embed_store.py` | Chunks the PDFs, creates embeddings and uploads them to Pinecone |
| `app.py` | Streamlit chat app |
| `requirements.txt` | Python dependencies |
| `.streamlit/secrets.toml` | API keys (keep out of Git) |

## Run It Locally

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

**2. Add your API keys** to `.streamlit/secrets.toml`

```toml
NVIDIA_API_KEY = "your_nvidia_key"
PINECONE_API_KEY = "your_pinecone_key"
GROQ_API_KEY = "your_groq_key"
```

> Add `.streamlit/secrets.toml` to your `.gitignore` so your keys are never pushed to GitHub.

**3. Create the documents and load them into Pinecone**

```bash
python create_sample_docs.py
python step3_embed_store.py
```

**4. Start the app**

```bash
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Push the project to GitHub (without `secrets.toml`).
2. Go to [share.streamlit.io](https://share.streamlit.io) and create a new app from your repository, with `app.py` as the main file.
3. Paste the three API keys into **App settings → Secrets**.
4. Deploy. You get a permanent `*.streamlit.app` link.

## Example Questions

- "How many days of annual leave do employees get?"
- "What is the password policy?"
- "What are the key features of the product?"

Each answer shows the source file and page, so you can verify it in the original PDF.
