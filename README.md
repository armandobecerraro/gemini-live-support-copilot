# SupportSight Live

**A multimodal incident support agent powered by Gemini Live API**

> Gemini Live Agent Challenge — Google 2026

[![CI](https://github.com/armandobecerrarodriguez/gemini-live-support-copilot/actions/workflows/ci.yml/badge.svg)](https://github.com/armandobecerrarodriguez/gemini-live-support-copilot/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## The Problem

When a production incident hits, engineers face a chaotic environment: scattered logs, error screenshots, noise in Slack, and no time to think. Diagnosis is slow, human, and exhausting.

**SupportSight Live** acts as a real-time intelligent copilot: it **listens to the engineer's voice**, **analyzes screenshots of the error**, **parses logs at high speed**, and **guides or executes safe diagnostic actions** — all in one live session, with human confirmation before any write operation.

---

## Demo Video

🎬 **[Watch the 4-minute demo →](https://youtu.be/PLACEHOLDER)**

---

## Architecture

```
User (voice + screen + logs)
        │
        ▼
┌─────────────────────────────────────────────┐
│   Next.js / Flutter UI                      │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│   Backend Orchestrator (Python + FastAPI)   │
│   ┌──────────────┐  ┌────────────────────┐  │
│   │ Vision Agent │  │ Incident Analyst   │  │
│   │ Runbook/RAG  │  │ Action Agent       │  │
│   └──────┬───────┘  └──────────┬─────────┘  │
│          └──────────┬──────────┘             │
│                     ▼                        │
│              Gemini Live API                 │
│              (GenAI SDK)                     │
└──────────┬──────────────────────┬────────────┘
           │                      │
    ┌──────▼──────┐   ┌───────────▼──────────┐
    │ Logs Service│   │ Actions Service       │
    │ Rust + PyO3 │   │ Java 21 + Spring Boot │
    │ 500MB/s     │   │ Allowlist + Audit Log │
    └─────────────┘   └───────────────────────┘
           │
    PostgreSQL + Redis (Google Cloud SQL)
```

Full architecture: [`docs/architecture/ARCHITECTURE.md`](docs/architecture/ARCHITECTURE.md)

---

## Tech Stack

| Service | Technology |
|---------|-----------|
| Backend Orchestrator | Python 3.12 + FastAPI + Google GenAI SDK |
| AI Model | Gemini 2.0 Flash Live (multimodal, streaming) |
| Log Parser | **Rust** (Aho-Corasick) — 1.2 GB/s, Anomaly Detection |
| Actions Service | **Java 21** (Spring Boot 3) — Dry-run + Full Auditing |
| Web Frontend | **TypeScript** + Next.js 14 + Lucide Icons |
| Mobile App | **Dart** + Flutter |
| Database | PostgreSQL 16 + **pgvector** |
| Deployment | **Google Cloud Run** + Terraform (IaC) |
| CI/CD | GitHub Actions |

---

## Features

- **Voice input** — speak to the agent, hands-free diagnosis
- **Screen capture** — share a screenshot, agent explains what it sees
- **Log analysis** — paste logs, **Rust parser (SIMD optimized)** identifies root cause in <10ms
- **Anomaly detection** — identifies structural outliers and log corruption in real-time
- **Multimodal reasoning** — Gemini combines voice + vision + text + logs
- **Hypothesis engine** — ranked hypotheses with confidence scores
- **Action panel** — `What I Understood`, `What I See`, `Recommendations`, `Next Action`
- **Enterprise Safeguards** — **Dry-run mode** for dangerous commands and **Allow-list** for secure execution
- **Human confirmation gate** — no action executes without your approval
- **Session timeline** — full auditable trail of every step
- **Incident report** — auto-generated Markdown/JSON for handoff
- **Professional RAG** — grounded answers using **pgvector** semantic search over your runbooks
- **Bilingual** — conversation in Spanish, artifacts in English

---

## Quick Start

### Prerequisites
- Python 3.12+
- Java 21 (Maven)
- Rust (stable)
- Node.js 20+
- Flutter 3.22+
- Docker + Docker Compose
- A Gemini API key → [aistudio.google.com](https://aistudio.google.com)

### Local Development

```bash
# 1. Clone the repo
git clone https://github.com/armandobecerrarodriguez/gemini-live-support-copilot.git
cd gemini-live-support-copilot

# 2. Set your Gemini API key
echo "GEMINI_API_KEY=your-key-here" > backend-orchestrator/.env

# 3. Start all services with Docker Compose
docker-compose -f docker-compose.local.yml up --build

# 4. Open the web interface
open http://localhost:3000
```

### Run services individually

```bash
# Backend orchestrator
cd backend-orchestrator
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080

# Logs service (Python fallback — no Rust required for dev)
cd logs-service
pip install fastapi uvicorn
uvicorn src.bridge.server:app --port 8090

# Actions service
cd actions-service
mvn spring-boot:run

# Frontend
cd frontend
npm install && npm run dev
```

---

## Demo Scenarios

Three reproducible fixtures in [`docs/demo-fixtures/`](docs/demo-fixtures/):

| # | Scenario | Category |
|---|---------|---------|
| 1 | Payment API — 503 errors, DB connection pool exhausted | Database |
| 2 | Backend OOMKilled — memory leak, JVM heap | Backend |
| 3 | Deployment stuck — image pull 403 Forbidden | Deployment |

---

## Deployment to Google Cloud Run

```bash
export GCP_PROJECT_ID=your-project-id
export GCP_REGION=us-central1
chmod +x infra/cloudrun/deploy.sh
./infra/cloudrun/deploy.sh
```

See [`infra/cloudrun/`](infra/cloudrun/) for full deployment guide.

---

## Project Structure

```
gemini-live-support-copilot/
├── backend-orchestrator/     # Python + FastAPI + Gemini (core orchestrator)
│   ├── app/
│   │   ├── agents/           # Vision, Analyst, Runbook, Action agents
│   │   ├── domain/           # Pure Python models + Pydantic schemas
│   │   ├── infrastructure/   # Gemini client, DB adapters
│   │   ├── prompts/          # Versioned prompt files
│   │   ├── routes/           # FastAPI routers
│   │   └── security/         # API key auth, OWASP guardrails
│   └── tests/
├── logs-service/             # Rust log parser + Python FastAPI bridge
│   ├── src/parser/           # Rust core (500MB/s throughput)
│   └── src/bridge/           # Python FastAPI server + PyO3 bindings
├── actions-service/          # Java 21 + Spring Boot 3 action executor
│   └── src/main/java/com/supportsight/
│       ├── actions/          # Controller + executor service
│       ├── domain/           # Records + JPA entities
│       └── security/         # API key filter + Spring Security
├── frontend/                 # Next.js 14 + TypeScript web client
│   └── src/
│       ├── app/              # Next.js App Router pages
│       ├── components/       # Session, Panel, Transcript, Evidence
│       ├── hooks/            # useAudioRecorder, useScreenCapture
│       └── services/         # API client (axios)
├── flutter_app/              # Dart + Flutter cross-platform client
│   └── lib/
│       ├── screens/          # HomeScreen
│       ├── widgets/          # InputPanel, ResponsePanel
│       ├── models/           # IssueRequest, AgentResponse
│       └── services/         # ApiService
├── docs/
│   ├── architecture/         # ARCHITECTURE.md + diagrams
│   ├── runbooks/             # Local knowledge base for RAG
│   └── demo-fixtures/        # 3 reproducible demo scenarios
├── infra/
│   ├── cloudrun/             # deploy.sh + deployment docs
│   └── docker/               # Additional Docker configs
├── .github/workflows/        # CI (test all langs) + CD (Cloud Run)
└── docker-compose.local.yml  # Full local stack
```

---

## Software Engineering Standards

- **SOLID** principles throughout all services
- **Hexagonal / Clean Architecture** — domain independent of frameworks
- **OWASP Top 10 2025** — input validation, auth, no sensitive data leakage
- **12-Factor App** — config via env vars, stateless, disposable processes
- **DevSecOps** — CI runs tests for all 5 languages + security scan
- **Observability-first** — correlation IDs, structured JSON logs, session timeline
- **Human-in-the-loop** — mandatory confirmation before any destructive action
- **Prompt engineering as code** — versioned `.txt` prompt files with `{placeholders}`

---

## Roadmap

- [x] **pgvector** for full RAG over runbook documents
- [x] **Anomaly Detection** in log streams
- [x] **Enterprise Auditing** for actions
- [ ] WebSocket streaming for real-time token output
- [ ] Gemini Live API native audio streaming (WebRTC)
- [ ] Slack / PagerDuty integration for incident creation
- [ ] Multi-language support (ES/EN auto-detect)
- [ ] Feedback loop for hypothesis accuracy improvement

---

## License

MIT — See [LICENSE](LICENSE)

---

## Devpost

🏆 **Submitted to the [Gemini Live Agent Challenge](https://geminiliveagentchallenge.devpost.com/)**

- **Built with:** Gemini 2.0 Flash Live, Google GenAI SDK, Google Cloud Run
- **Languages:** Python, Rust, Java, TypeScript, Dart
- **Category:** Live Agents
