<div align="center">

# Talk to Your Data

### Natural Language to SQL Analytics Assistant

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=20&pause=1200&color=7B2CBF&center=true&vCenter=true&width=850&height=50&lines=Ask+questions+in+plain+English;Generate+safe+SQL+automatically;Execute%2C+visualize+and+explain+results" alt="Typing Animation"/>

<br/>

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
<img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white"/>
<img src="https://img.shields.io/badge/LLM-7B2CBF?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"/>

<br/><br/>

**Natural Language → SQL → Validation → Execution → Visualization → Explanation**

</div>

---

## 1. Overview

**Talk to Your Data** is a production-oriented Text-to-SQL application that allows non-technical users to query structured business data using natural language.

Instead of requiring users to understand SQL syntax, database schemas, joins or aggregations, the system translates a natural-language question into SQL, validates the generated query, executes it against PostgreSQL, and presents the result in an understandable format.

### Example

A business user can ask:

```text
Which out-of-stock products have the highest estimated revenue?
```

The system transforms the request into:

```text
Natural Language Question
        ↓
Database Schema Context
        ↓
LLM SQL Generation
        ↓
SQL Validation
        ↓
PostgreSQL Execution
        ↓
Result Table + Visualization
        ↓
Plain-English Explanation
```

The project focuses not only on SQL generation, but on the engineering required to make **LLM-generated database queries safer, testable and recoverable**.

---

## 2. Problem Statement

Traditional business analytics often requires users to depend on analysts or engineers for relatively simple database questions.

A typical workflow looks like:

```text
Business Question
       ↓
Analyst
       ↓
Understand Database Schema
       ↓
Write SQL
       ↓
Run Query
       ↓
Clean / Format Results
       ↓
Create Visualization
       ↓
Explain Findings
```

This creates unnecessary friction for exploratory analysis.

The goal of this project is to introduce a natural-language interface while preserving important database safety constraints.

### The system should:

* Understand natural-language analytical questions
* Generate syntactically valid SQL
* Use the actual database schema
* Restrict execution to safe read-only operations
* Recover from SQL execution errors
* Return structured results
* Generate appropriate visualizations
* Explain results in plain English
* Provide measurable evaluation rather than relying on subjective quality

---

# 3. System Architecture

```text
                         ┌──────────────────────┐
                         │       User           │
                         │ Natural Language     │
                         │      Question        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     FastAPI API      │
                         │   Request Handling   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Schema Provider      │
                         │                      │
                         │ Tables               │
                         │ Columns              │
                         │ Data Types           │
                         │ Sample Values        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     LLM Layer        │
                         │                      │
                         │ Natural Language     │
                         │        ↓             │
                         │       SQL            │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    SQL Validator     │
                         │                      │
                         │ SELECT / WITH only  │
                         │ Row limits           │
                         │ Forbidden operations │
                         └──────────┬───────────┘
                                    │
                              ┌─────┴─────┐
                              │           │
                           Valid       Invalid
                              │           │
                              ▼           ▼
                       ┌───────────┐   Reject
                       │PostgreSQL │
                       └─────┬─────┘
                             │
                        ┌────┴─────┐
                        │          │
                     Success     Error
                        │          │
                        │          ▼
                        │     Error Context
                        │          │
                        │          ▼
                        │         LLM
                        │          │
                        │          ▼
                        │      Corrected SQL
                        │
                        ▼
                 ┌──────────────────┐
                 │ Result Processor  │
                 └────────┬─────────┘
                          │
                ┌─────────┼─────────┐
                ▼         ▼         ▼
              Table     Chart    Explanation
                │         │         │
                └─────────┼─────────┘
                          ▼
                    Final Response
```

---

# 4. Core Workflow

## Step 1 — Receive the Question

The user submits an analytical question through the application interface.

Example:

```text
Which products are currently out of stock and have the
highest estimated revenue?
```

The application forwards the request to the backend.

---

## Step 2 — Retrieve Database Schema

The application constructs a schema context containing relevant database information.

The context can include:

```text
Table Names
Column Names
Data Types
Relationships
Sample Values
```

Example:

```text
products
---------
product_id
product_name
category
price
stock_quantity
```

Schema information is injected into the LLM prompt before SQL generation.

This reduces the probability of the model inventing tables or columns that do not exist.

---

# 5. SQL Generation

The LLM receives the user question together with the database schema.

Conceptually:

```text
System Instructions
        +
Datab
```
