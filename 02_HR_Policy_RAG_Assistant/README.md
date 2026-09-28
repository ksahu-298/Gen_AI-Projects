# HR Policy Assistant (RAG)

A retrieval-augmented generation (RAG) chatbot that answers employee questions about a company's HR policy document. Built with **LangChain**, **Groq**-hosted LLMs, **Jina** embeddings, and a **FAISS** vector store, with input/output safety guardrails and **LangSmith** tracing.

**Live Demo:** [hr-rag-assist.streamlit.app](https://hr-rag-assist.streamlit.app/)

---

## How It Works

1. **Ingest** — `hr_assistant/document_loader.py` loads `data/hr_policy.txt`, and `hr_assistant/splitter.py` splits it into chunks (`CHUNK_SIZE=500`, `CHUNK_OVERLAP=60`).
2. **Embed & store** — `hr_assistant/embeddings.py` creates embeddings with Jina (`jina-embeddings-v2-base-en`), and `hr_assistant/vector_store.py` builds/loads a local FAISS index (persisted to disk and reused on subsequent runs instead of re-embedding).
3. **Retrieve** — `hr_assistant/tools.py` wraps the vector store retriever (top-k = 3) as a `search_hr_policy` tool.
4. **Agent** — `hr_assistant/agent.py` builds a LangChain agent (`openai/gpt-oss-20b` via Groq) that calls the search tool to ground its answers.
5. **Guardrails** — `hr_assistant/guardrails.py` runs a separate Groq safety model (`openai/gpt-oss-safeguard-20b`) to screen both the incoming question (prompt injection, requests for other employees' data) and the outgoing answer (PII leaks, unauthorized promises, suspicious links) before it reaches the user.
6. Everything is wired together in `hr_assistant/pipeline.py` (`build_hr_assistant()` / `ask()`), used by both entry points below.

---

## Entry Points

| Command | Description |
|---|---|
| `python main.py` | CLI demo that asks a few sample HR questions |
| `streamlit run app.py` | Interactive chat UI |
| `rag.ipynb` | Notebook version for experimentation |

---

## Project Layout

```
hr_assistant/
  config.py          settings, env vars, system prompt
  document_loader.py load the HR policy text file
  splitter.py         chunk the document
  embeddings.py       Jina embeddings model
  vector_store.py     FAISS index build/load/retriever
  tools.py             search tool for the agent
  llm.py                Groq LLM setup
  agent.py             LangChain agent construction
  guardrails.py        input/output safety checks
  pipeline.py           wires everything together (build_hr_assistant, ask)
  logger.py             file logging (logs/)
  tracing.py             LangSmith tracing check
data/hr_policy.txt      source HR policy document
docs/                    notes on logging, LangSmith, FAISS setup, guardrail attack testing
NOTES/                   reference PDFs
```

---

## Tech Stack

- **Orchestration:** LangChain (agent framework)
- **LLM (agent):** `openai/gpt-oss-20b` via Groq
- **LLM (guardrails):** `openai/gpt-oss-safeguard-20b` via Groq
- **Embeddings:** Jina (`jina-embeddings-v2-base-en`)
- **Vector Store:** FAISS (local, persisted to disk)
- **UI:** Streamlit
- **Tracing/Observability:** LangSmith
- **Package management:** [uv](https://github.com/astral-sh/uv)

---

## Setup

### 1. Install [uv](https://github.com/astral-sh/uv)

```bash
pip install uv
```

### 2. Create and activate a virtual environment

```bash
uv venv ragenv
ragenv\Scripts\activate
```

> On macOS/Linux use: `source ragenv/bin/activate`

### 3. Install dependencies

```bash
uv pip install -r requirements.txt
```

### 4. Create a `.env` file

```env
GROQ_API_KEY=...
JINA_API_KEY=...
FAISS_INDEX_PATH=...
LANGSMITH_TRACING=false
LANGSMITH_ENDPOINT=...
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=...
```

> Adjust `FAISS_INDEX_PATH` (or equivalent variable name in `config.py`) to match wherever `vector_store.py` persists the index on disk.

### 5. Run it

```bash
# CLI demo
python main.py

# Streamlit chat UI
streamlit run app.py
```

---

## Safety Guardrails

Every interaction is screened twice by a dedicated Groq safety model (`openai/gpt-oss-safeguard-20b`):

- **Input check:** blocks prompt injection attempts and requests for other employees' private data.
- **Output check:** blocks PII leaks, unauthorized promises, and suspicious links before an answer reaches the user.

See `docs/` for notes on guardrail attack testing.

---

## Observability

LangSmith tracing can be toggled via `LANGSMITH_TRACING` in `.env`. When enabled, runs are logged to the configured `LANGSMITH_PROJECT` for debugging and evaluation. Local file logging is also handled via `hr_assistant/logger.py` (written to `logs/`).

---

## Git Basics

```bash
git add .
git commit -m "Some message"
git push
```

---

## Docs

The `docs/` folder contains supplementary notes on:
- Logging setup
- LangSmith integration
- FAISS index setup/persistence
- Guardrail attack testing

Reference PDFs live in `NOTES/`.
