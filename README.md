# Apex Manufacturing AI

An end-to-end AI-powered manufacturing intelligence platform that combines analytics, machine learning, RAG, and a natural-language AI agent.

---

## Overview

Apex Manufacturing AI allows users to ask natural-language questions about a manufacturing operation.

The system can analyze:

- Production
- Production efficiency
- Machines
- Machine failures
- Downtime
- Quality
- Sensor readings
- Maintenance
- Manufacturing documentation

The project combines structured database analysis, machine-learning predictions, retrieval-augmented generation, and a Groq-powered AI agent.

---

# Architecture

```text
                    ┌──────────────────────┐
                    │    Web Dashboard     │
                    │     HTML/CSS/JS      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       FastAPI        │
                    │       REST API       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     Groq AI Agent    │
                    │  Natural Language AI │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
       Manufacturing       ML Failure       RAG Knowledge
           Tools            Prediction         Retrieval
              │                │                │
              └────────────────┼────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    SQLite Database   │
                    │  Manufacturing Data  │
                    └──────────────────────┘