<div align="center">

# 🧠 Gen AI Projects

### Production-oriented Generative AI systems built with Python

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=20&pause=1200&color=7B2CBF&center=true&vCenter=true&width=750&height=50&lines=Text-to-SQL+%7C+RAG+%7C+AI+Agents;LLMs+with+Guardrails%2C+Tools+%26+Evals;Building+Reliable+GenAI+Systems" alt="Typing SVG"/>

<br/>

<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/LLM-7B2CBF?style=flat-square"/>
<img src="https://img.shields.io/badge/RAG-2E8B57?style=flat-square"/>
<img src="https://img.shields.io/badge/LangGraph-1C1C1C?style=flat-square"/>
<img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white"/>

</div>

---

## 🚀 About

A collection of **three practical Generative AI projects** focused on building reliable, testable and production-oriented LLM applications.

Rather than treating an LLM as a standalone chatbot, these projects explore how to build complete AI systems around it — with **retrieval, tools, validation, evaluation, observability and human oversight**.

---

## 🧩 Projects

| #      | Project                   | Focus                               | Status      |
| ------ | ------------------------- | ----------------------------------- | ----------- |
| **01** | 🗃️ **Talk to Your Data** | Natural Language → SQL              | 🚧 Building |
| **02** | 🔎 **Production RAG Q&A** | Retrieval + Citations + Evals       | 🚧 Building |
| **03** | 🤖 **Support Agent**      | Tools + Guardrails + Human Approval | 🚧 Building |

---

### 01 · 🗃️ Talk to Your Data

**Text-to-SQL assistant for business analytics**

Ask questions in natural language and receive:

`Question → SQL → Results → Chart → Explanation`

**Key engineering features**

* Schema-aware SQL generation
* Read-only query validation
* PostgreSQL execution
* Automatic SQL error correction
* Query limits and safety controls
* Evaluation set with known answers

**Stack:** `FastAPI` `PostgreSQL` `LLM API` `Streamlit/React` `Docker`

➡️ **[Explore Project →](./01_Text_to_SQL)**

---

### 02 · 🔎 Production RAG Q&A

**Document-grounded Q&A with citations**

`Documents → Chunking → Hybrid Retrieval → Reranking → LLM → Citations`

**Key engineering features**

* Fixed vs structure-aware chunking
* Vector + keyword hybrid search
* Reranking
* Page-level citations
* "I don't know" refusal path
* Retrieval and faithfulness evaluation

**Stack:** `FastAPI` `ChromaDB/pgvector` `Reranker` `RAGAS` `Docker`

➡️ **[Explore Project →](./02_Production_RAG)**

---

### 03 · 🤖 Support Agent

**Tool-using e-commerce support agent**

`Intent → Tools → Guardrails → Human Approval → Response`

**Key engineering features**

* Order lookup
* Policy retrieval
* Refund tool
* LangGraph workflow
* Human-in-the-loop approval
* Agent tracing and evaluation

**Stack:** `LangGraph` `FastAPI` `PostgreSQL` `Langfuse` `Docker`

➡️ **[Explore Project →](./03_Support_Agent)**

---

## 🏗️ Engineering Principles

```text
             ┌──────────────────────┐
             │       LLM            │
             └──────────┬───────────┘
                        │
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
   Guardrails        Retrieval          Tools
        │               │                │
        └───────────────┼────────────────┘
                        ▼
                    Evaluation
                        │
                        ▼
                   Observability
                        │
                        ▼
               Production System
```

### 🔐 Safety First

Validate model-generated SQL, restrict database permissions and control tool execution.

### 📊 Measure Everything

Every project includes an evaluation strategy instead of relying solely on subjective LLM output.

### 🧪 Design for Failure

Document retrieval failures, invalid SQL, hallucinations, tool errors and unsupported requests.

### 👤 Human Oversight

High-impact actions should have explicit approval boundaries.

### 🚀 Production Mindset

Containerization, environment variables, logging, testing and deployment are part of the design.

---

## 🛠️ Core Technologies

```text
Python
├── FastAPI
├── LangGraph
├── RAG / Vector Search
├── LLM APIs
├── RAGAS
└── Langfuse

Data
├── PostgreSQL
├── ChromaDB / pgvector
└── SQL

Engineering
├── Docker
├── Git / GitHub
├── Testing
└── Evaluation
```

---

## 📈 Evaluation Philosophy

Performance numbers will be added **only after measurement**.

Examples of metrics tracked across the projects:

* SQL execution accuracy
* Retrieval hit rate
* Faithfulness
* Citation correctness
* Task success rate
* Tool-call accuracy
* Guardrail accuracy
* Latency
* Failure rate

> **No fabricated benchmarks. Build → Evaluate → Improve → Measure again.**

---

## 🔐 Security

Secrets and sensitive data are never committed.

```text
✓ .env / environment variables
✓ .env.example
✓ .gitignore
✓ Read-only database access
✓ Query validation
✓ Tool authorization
✓ No real customer data
```

---

## 🗺️ Roadmap

* [ ] Build Text-to-SQL system
* [ ] Create SQL evaluation dataset
* [ ] Build production RAG pipeline
* [ ] Add retrieval evaluation
* [ ] Build LangGraph support agent
* [ ] Implement human approval workflow
* [ ] Add Langfuse tracing
* [ ] Containerize applications
* [ ] Deploy projects
* [ ] Publish evaluation results

---

<div align="center">

### ⚡ Build. Evaluate. Improve.

**Turning LLM capabilities into reliable AI systems.**

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:7B2CBF,100:06B6D4&height=100&section=footer" width="100%"/>

</div>
