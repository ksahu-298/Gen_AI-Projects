<div align="center">

# 🧠 Gen_AI Projects

### Production-Oriented Generative AI Systems

<img src="https://readme-typing-svg.demolab.com/?font=Fira+Code&weight=600&size=21&pause=900&color=7B2CBF&center=true&vCenter=true&width=900&height=55&lines=Text-to-SQL+%7C+Production+RAG+%7C+Tool-Using+Agents;Building+GenAI+Systems+with+Guardrails+%26+Evals;From+LLM+Demos+to+Production-Oriented+AI" alt="Typing SVG"/>

<br/>

<img src="https://img.shields.io/badge/GenAI-7B2CBF?style=for-the-badge"/>
<img src="https://img.shields.io/badge/LLM%20Applications-2F81F7?style=for-the-badge"/>
<img src="https://img.shields.io/badge/RAG-00A67E?style=for-the-badge"/>
<img src="https://img.shields.io/badge/AI%20Agents-E67E22?style=for-the-badge"/>

</div>

---

## 🎯 Repository Overview

This repository contains **three production-oriented Generative AI projects** designed around practical business use cases rather than simple LLM demonstrations.

The projects explore three increasingly capable patterns:

```text
┌─────────────────────────────────────────────────────────────┐
│                    GEN AI SYSTEMS                            │
└─────────────────────────────────────────────────────────────┘

        01                         02                     03
        │                          │                      │
        ▼                          ▼                      ▼
   TEXT → SQL                 PRODUCTION RAG        TOOL-USING AGENT
        │                          │                      │
        ▼                          ▼                      ▼
   Structured Data             Documents            External Tools
        │                          │                      │
        ▼                          ▼                      ▼
   SQL + Results              Cited Answers        Actions + Approval
        │                          │                      │
        ▼                          ▼                      ▼
   Self-Correction             Evals + Refusal      Human-in-the-Loop
```

### Core engineering themes

* 🔐 **Safety & Guardrails**
* 📊 **Evaluation & Measurement**
* 🔄 **Self-Correction**
* 🔎 **Retrieval & Reranking**
* 🛠️ **Tool Calling**
* 👤 **Human-in-the-Loop**
* 📈 **Observability & Tracing**
* 🚀 **Deployment & Production Readiness**

---

# 01 · 🗃️ Text-to-SQL — "Talk to Your Data"

### Natural Language → SQL → Results → Visualization → Explanation

> Ask questions about business data in plain English without knowing SQL.

### 💡 Use Case

A business user—such as a category manager at a quick-commerce company—can ask:

> **"Which out-of-stock products have the highest estimated revenue?"**

The system generates the appropriate SQL, executes it safely, presents the result as a table/chart, and explains the answer in plain English.

---

## 🔄 Architecture

```text
             USER QUESTION
                   │
                   ▼
        ┌─────────────────────┐
        │ Schema Injection    │
        │ Tables / Columns    │
        │ Sample Values       │
        └──────────┬──────────┘
                   │
                   ▼
             ┌─────────┐
             │   LLM   │
             └────┬────┘
                  │
                  ▼
           Generated SQL
                  │
                  ▼
        ┌───────────────────┐
        │ SQL VALIDATOR     │
        │                   │
        │ ✓ SELECT only     │
        │ ✓ Row limit       │
        │ ✗ DROP            │
        │ ✗ DELETE          │
        │ ✗ UPDATE          │
        └─────────┬─────────┘
                  │
                  ▼
             PostgreSQL
                  │
             ┌────┴────┐
             │         │
          Success     Error
             │         │
             │         ▼
             │    Error → LLM
             │         │
             │         └──► Retry
             │
             ▼
       Result Dataset
             │
        ┌────┴─────┐
        ▼          ▼
      Table      Chart
        │          │
        └────┬─────┘
             ▼
       Plain-English
         Explanation
```

---

## 🧠 Key Engineering Features

### 1. Schema-Aware Generation

The LLM receives:

* Table names
* Column names
* Data types
* Sample values

This reduces hallucinated table/column names and improves SQL generation.

### 2. SQL Safety Layer

Generated SQL is validated before execution.

```text
Allowed:
✓ SELECT
✓ WITH
✓ Aggregations
✓ JOINs
✓ GROUP BY
✓ ORDER BY

Blocked:
✗ DROP
✗ DELETE
✗ UPDATE
✗ INSERT
✗ ALTER
✗ TRUNCATE
```

Additional protection:

* Read-only PostgreSQL user
* Query row limit
* Query validation
* Controlled database access

### 3. Self-Correction Loop

```text
LLM
 │
 ▼
SQL
 │
 ▼
Execute
 │
 ├── SUCCESS ──► Result
 │
 └── ERROR
       │
       ▼
   Error Message
       │
       ▼
      LLM
       │
       ▼
   Corrected SQL
```

### 4. Evaluation Set

A dedicated evaluation dataset will contain:

**30–50 natural-language questions**

Each question will have:

* Expected SQL
* Generated SQL
* Execution result
* Correctness
* Failure reason

### 📏 Metrics

> **Execution Accuracy:** `[TO BE MEASURED]`

> **Before schema samples:** `[TO BE MEASURED]`

> **After schema samples:** `[TO BE MEASURED]`

> **Self-correction improvement:** `[TO BE MEASURED]`

**Metrics will only be added after evaluation is actually performed.**

---

## 🛠️ Stack

```text
FastAPI
PostgreSQL
LLM API
Streamlit / React
Docker
Python
```

---

# 02 · 🔎 Production RAG Q&A with Evals

### Ask Questions → Retrieve Evidence → Generate Cited Answers

> A production-oriented RAG system designed to answer questions from a controlled document collection while refusing to answer when sufficient evidence is unavailable.

---

## 💡 Use Case

Employees or customers can ask questions over a large document collection such as:

* Company annual reports
* Insurance policy documents
* Software documentation
* Internal knowledge bases

The system returns:

**Answer + Page-Level Citations**

When the required information isn't available:

> **"I don't know based on the provided documents."**

---

## 🔄 Architecture

```text
                  DOCUMENTS
                      │
                      ▼
              ┌──────────────┐
              │ PDF Ingestion │
              └──────┬───────┘
                     │
                     ▼
             Document Chunking
                     │
             ┌───────┴────────┐
             │                │
       Fixed-Size        Structure-Aware
       Chunking            Chunking
             │                │
             └───────┬────────┘
                     ▼
                 Embeddings
                     │
                     ▼
              Vector Database
              ChromaDB/pgvector
                     │
                     ▼
              ┌──────────────┐
              │ Hybrid Search│
              │              │
              │ Keyword      │
              │ + Vector     │
              └──────┬───────┘
                     │
                     ▼
                  Reranker
                     │
                     ▼
              Retrieved Context
                     │
                     ▼
                   LLM
                     │
              ┌──────┴──────┐
              ▼             ▼
          Supported      Unsupported
              │             │
              ▼             ▼
       Cited Answer     "I don't know"
```

---

## 🧠 Key Engineering Features

### 📚 Chunking Comparison

The system evaluates:

**Fixed-size chunking**

vs.

**Structure-aware chunking**

The objective is to measure whether document structure improves retrieval quality.

---

### 🔎 Hybrid Retrieval

Combines:

```text
Keyword Search
      +
Vector Search
      ↓
Candidate Documents
      ↓
Reranking
      ↓
Best Context
```

This allows the system to benefit from both lexical matching and semantic similarity.

---

### 📌 Page-Level Citations

Answers are grounded in retrieved document sections and include page-level references.

```text
Question
   ↓
Retrieved Chunks
   ↓
LLM Answer
   ↓
Citation
   └──► Document + Page
```

---

### 🛑 Refusal Path

The system should **not manufacture an answer** when the retrieved evidence does not support the question.

```text
Question
   │
   ▼
Retrieve
   │
   ▼
Sufficient Evidence?
   │
 ┌─┴─────────┐
YES          NO
 │            │
 ▼            ▼
Answer      REFUSE
+ Citations
```

---

## 📊 Evaluation

A dedicated **50-question evaluation set** will measure:

* Retrieval hit rate
* Faithfulness
* Answer quality
* Citation correctness
* Refusal behavior

### Improvement Tracking

| Configuration            | Retrieval Hit Rate |       Faithfulness |
| ------------------------ | -----------------: | -----------------: |
| Baseline                 | `[TO BE MEASURED]` | `[TO BE MEASURED]` |
| Structure-aware chunking | `[TO BE MEASURED]` | `[TO BE MEASURED]` |
| Hybrid search            | `[TO BE MEASURED]` | `[TO BE MEASURED]` |
| + Reranking              | `[TO BE MEASURED]` | `[TO BE MEASURED]` |

---

## 🔬 Failure Analysis

The README will document real failure cases discovered during evaluation.

Examples of areas to investigate:

* Poor chunk boundaries
* Missing context
* Incorrect retrieval
* Citation mismatch
* Hallucinated answers
* Questions outside the document corpus

**Failures will be documented after testing rather than fabricated beforehand.**

---

## 🛠️ Stack

```text
FastAPI
ChromaDB / pgvector
Embedding Model
Reranker Model
LLM API
RAGAS
Docker
Python
```

---

# 03 · 🤖 Support Agent with Tools + Human Approval

### Tool-Using AI Agent with Guardrails

> An e-commerce support agent capable of retrieving information, searching policies, initiating refunds, and escalating sensitive actions to humans.

---

## 💡 Use Case

The support agent handles:

* 📦 Order-status questions
* 📋 Return-policy questions
* 💰 Refund requests
* ❓ Unknown or unsupported requests

It can use external tools but **doesn't have unrestricted authority**.

---

## 🔄 Agent Architecture

```text
                  USER
                   │
                   ▼
            Intent Classifier
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
      STATUS     POLICY      REFUND
        │          │          │
        ▼          ▼          ▼
     Order DB    Policy RAG   Refund Tool
        │          │          │
        │          │          ▼
        │          │      Guardrail
        │          │          │
        │          │    ┌─────┴─────┐
        │          │    ▼           ▼
        │          │  Below       Above
        │          │  Threshold   Threshold
        │          │    │           │
        │          │    ▼           ▼
        │          │  Execute    HUMAN APPROVAL
        │          │                │
        └──────────┴────────────────┘
                         │
                         ▼
                    Final Response
                         │
                         ▼
                       Trace
```

---

## 🧰 Agent Tools

### 📦 Order Lookup

Retrieves order information from PostgreSQL.

### 📚 Policy Search

Uses a small RAG pipeline to retrieve relevant return/refund policies.

### 💰 Refund Tool

Mock API capable of processing refunds subject to business rules.

---

## 👤 Human-in-the-Loop

Sensitive actions require human approval.

Example:

```text
Refund Request
      │
      ▼
Amount < Threshold?
      │
 ┌────┴─────┐
YES         NO
 │           │
 ▼           ▼
Execute    PAUSE
Refund       │
             ▼
      Human Approval
             │
       ┌─────┴─────┐
       ▼           ▼
    Approved     Rejected
       │           │
       ▼           ▼
    Refund       Escalate
```

This creates a clear boundary between:

**AI autonomy** and **human authority**.

---

## 🧠 LangGraph Workflow

The agent is designed around explicit state transitions rather than a single uncontrolled LLM loop.

```text
START
  │
  ▼
Intent
  │
  ▼
Tool Selection
  │
  ▼
Tool Execution
  │
  ▼
Guardrail
  │
  ├──► Continue
  │
  └──► Human Approval
            │
            ▼
         Resume
            │
            ▼
        Response
            │
            ▼
           END
```

---

## 📊 Agent Evaluation

A scripted evaluation suite will contain:

**40–50 conversations**

Testing areas such as:

* Correct intent classification
* Correct tool selection
* Accurate order retrieval
* Correct policy retrieval
* Refund handling
* Guardrail enforcement
* Human escalation
* Unsupported requests

### Target Metric

> **Task Success Rate:** `[TO BE MEASURED]`

Additional metrics:

* Tool-call accuracy: `[TO BE MEASURED]`
* Escalation accuracy: `[TO BE MEASURED]`
* Policy retrieval accuracy: `[TO BE MEASURED]`
* Failure rate: `[TO BE MEASURED]`

---

## 🔭 Observability

Every agent execution should be traceable.

```text
User Request
     │
     ▼
Intent Classification
     │
     ▼
Tool Selection
     │
     ▼
Tool Input
     │
     ▼
Tool Output
     │
     ▼
Guardrail
     │
     ▼
Final Response
```

**Langfuse** will be used to inspect traces, identify failures and improve the workflow.

---

## 🛠️ Stack

```text
LangGraph
FastAPI
PostgreSQL
Langfuse
Docker
Python
```

### Optional Extension

```text
MCP Server
     │
     ├── Order Lookup Tool
     ├── Policy Tool
     └── Refund Tool
```

---

# 📊 Cross-Project Engineering Principles

All three projects follow the same philosophy:

### 01 — Don't Trust the LLM

LLMs generate outputs.

**Systems validate them.**

---

### 02 — Measure Before Claiming

Every project contains an evaluation layer.

```text
Build
  ↓
Test
  ↓
Measure
  ↓
Identify Failure
  ↓
Improve
  ↓
Measure Again
```

No performance metric is added to the README until it has actually been measured.

---

### 03 — Design for Failure

Each project explicitly considers failure:

| Project       | Failure Handling               |
| ------------- | ------------------------------ |
| Text-to-SQL   | SQL validation + retry         |
| RAG           | Retrieval evaluation + refusal |
| Support Agent | Guardrails + human approval    |

---

### 04 — Keep Secrets Out of Git

Sensitive credentials are never committed.

```text
.env
.env.local
secrets/
*.pem
*.key
```

Use environment variables for:

* API keys
* Database credentials
* Application secrets
* Deployment configuration

---

# 🔐 Security Checklist

```text
✓ Environment variables for secrets
✓ .gitignore configured
✓ No real customer/patient/company data
✓ Read-only DB access where possible
✓ SQL query validation
✓ Query limits
✓ Tool authorization
✓ Human approval for sensitive actions
✓ Logging without exposing secrets
```

---

# 🐳 Deployment

Each project is designed to be containerized.

```text
Application
     │
     ▼
  Docker
     │
 ┌───┴─────────────┐
 ▼                 ▼
Backend          Database
 │                 │
 ▼                 ▼
API / UI       PostgreSQL
```

### Deployment Status

| Project        | Status      | Live Demo    |
| -------------- | ----------- | ------------ |
| Text-to-SQL    | 🚧 Building | `[ADD LINK]` |
| Production RAG | 🚧 Building | `[ADD LINK]` |
| Support Agent  | 🚧 Building | `[ADD LINK]` |

> Live URLs will be added after successful deployment and testing.

---

# 📁 Repository Structure

```text
Gen_AI-Projects/
│
├── 01_Text_to_SQL/
│   ├── app/
│   ├── database/
│   ├── evaluation/
│   ├── frontend/
│   ├── tests/
│   ├── Dockerfile
│   ├── .env.example
│   ├── .gitignore
│   └── README.md
│
├── 02_Production_RAG/
│   ├── app/
│   ├── ingestion/
│   ├── retrieval/
│   ├── evaluation/
│   ├── documents/
│   ├── tests/
│   ├── Dockerfile
│   ├── .env.example
│   ├── .gitignore
│   └── README.md
│
├── 03_Support_Agent/
│   ├── agent/
│   ├── tools/
│   ├── rag/
│   ├── evaluation/
│   ├── traces/
│   ├── tests/
│   ├── Dockerfile
│   ├── .env.example
│   ├── .gitignore
│   └── README.md
│
└── README.md
```

---

# 🗺️ Project Roadmap

```text
                    GEN AI PORTFOLIO
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
      TEXT-to-SQL        RAG             AGENTS
          │                │                │
          ▼                ▼                ▼
       Safety          Retrieval          Tools
          │                │                │
          ▼                ▼                ▼
     Self-Correction     Evals          Guardrails
          │                │                │
          ▼                ▼                ▼
      Analytics        Citations       Human Approval
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                 PRODUCTION GENAI
```

---

## 🚀 Future Improvements

* [ ] Deploy all three projects
* [ ] Complete automated evaluation suites
* [ ] Add CI/CD pipelines
* [ ] Add structured application logging
* [ ] Add latency and cost tracking
* [ ] Add authentication where required
* [ ] Add automated regression tests
* [ ] Add MCP integration to the support agent
* [ ] Compare multiple LLM providers/models
* [ ] Publish evaluation results
* [ ] Document production failure cases

---

<div align="center">

## 🧠 From LLM Demos to Reliable AI Systems

**Safety • Retrieval • Tools • Evaluation • Observability • Human Oversight**

<br/>

⭐ **Built by Karan Sahu**

</div>

