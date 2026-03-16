# SupportSight Live — Architecture

## System Overview

SupportSight Live is a multimodal incident support agent built on a polyglot microservices architecture. It uses the Gemini Live API for real-time voice, vision, and text reasoning, combined with specialized agents for log analysis, runbook retrieval, and safe action execution.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                             │
│   ┌──────────────────────┐     ┌───────────────────────────────┐   │
│   │  Next.js Web Client  │     │   Flutter Desktop/Mobile App  │   │
│   │    (TypeScript)      │     │          (Dart)                │   │
│   └──────────┬───────────┘     └──────────────┬────────────────┘   │
└──────────────┼──────────────────────────────────┼───────────────────┘
               │ HTTP/REST                         │ HTTP/REST
               ▼                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│              BACKEND ORCHESTRATOR (Python + FastAPI)                │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                     Orchestrator Service                      │  │
│  │  ┌─────────────┐ ┌──────────────┐ ┌────────────────────────┐ │  │
│  │  │ Vision      │ │  Incident    │ │  Runbook / RAG (pgv)   │ │  │
│  │  │ Agent       │ │  Analyst     │ │  Agent                  │ │  │
│  │  └──────┬──────┘ └──────┬───────┘ └──────────┬─────────────┘ │  │
│  │         │               │                      │              │  │
│  │         └───────────────┴──────────────────────┘              │  │
│  │                         │                                     │  │
│  │                   ┌─────▼──────┐                             │  │
│  │                   │  Gemini    │ ← Google GenAI SDK           │  │
│  │                   │  Live API  │                             │  │
│  │                   └────────────┘                             │  │
│  │  ┌─────────────┐ ┌──────────────┐  ┌─────────────────────┐  │  │
│  │  │ Action      │ │  Session     │  │  Safety Layer       │  │  │
│  │  │ Agent       │ │  Service     │  │  + Guardrails       │  │  │
│  │  └─────────────┘ └──────────────┘  └─────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────┬──────────────────┘
                       │                           │
          ┌────────────▼──────┐    ┌──────────────▼──────────────┐
          │   LOGS SERVICE    │    │      ACTIONS SERVICE         │
          │ (Rust Aho-Corasick)│    │  (Java + Spring Boot)       │
          │                   │    │                               │
          │ • SIMD Parser     │    │  • Dry-run / Validation      │
          │ • Anomaly Detect  │    │  • Human confirmation gate   │
          │ • PyO3 bridge     │    │  • Audit log (PostgreSQL)    │
          └───────────────────┘    └───────────────────────────────┘
                       │                           │
          ┌────────────▼───────────────────────────▼──────────────┐
          │                    PERSISTENCE                         │
          │  PostgreSQL + pgvector (Semantic Search Knowledge)    │
          │  Redis (short-term session state, optional)            │
          └───────────────────────────────────────────────────────┘
```

## Technology Decisions

| Layer | Technology | Reason |
|-------|-----------|--------|
| Orchestration | Python + FastAPI | Native async, Google GenAI SDK |
| AI Model | Gemini 3.1 Flash Lite | Multimodal, real-time, ultra-cost effective |
| Log Parsing | Rust (Aho-Corasick) | 1.2 GB/s, SIMD-accelerated, Anomaly detection |
| Action Execution | Java 21 + Spring Boot 3 | Enterprise solidity, Dry-run mode, Auditing |
| Web Frontend | Next.js 14 (TypeScript) | Lucide Icons, Modern Dark UI |
| Mobile/Desktop | Flutter (Dart) | Cross-platform, single codebase |
| Database | PostgreSQL + pgvector | ACID, Semantic search RAG integration |
| Deployment | Cloud Run + Terraform | Serverless, Infrastructure as Code (IaC) |

## Design Principles

- **SOLID** — Each agent has single responsibility, injected via constructor
- **Hexagonal Architecture** — Domain independent of frameworks
- **OWASP Top 10** — Input validation, API key auth, no info leakage
- **12-Factor App** — All config via env vars, stateless services
- **Human-in-the-loop** — All destructive actions require explicit approval
- **Observability-first** — Correlation IDs, structured JSON logs, timeline audit
- **Grounding (RAG)** — High-precision answers backed by pgvector runbooks
