# SupportSight Live

**A multimodal, real-time incident support agent powered by the Gemini Live API.**

> Built for the **Gemini Live Agent Challenge — Google 2026**

[![CI](https://github.com/armandobecerraro/supportsight-live-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/armandobecerraro/supportsight-live-agent/actions)
[![CD](https://github.com/armandobecerraro/supportsight-live-agent/actions/workflows/cd.yml/badge.svg)](https://github.com/armandobecerraro/supportsight-live-agent/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🌟 Try the Live Demo

**[Launch SupportSight Live on Google Cloud Run](https://supportsight-frontend-k7r3xdbakq-uc.a.run.app)**  
*(Click "Guide" in the web app to access ready-to-run incident examples).*

🎬 **[Watch the demo on YouTube →](https://www.youtube.com/watch?v=FR2o6YuF62Y)**

---

## 🚨 The Problem

When a production incident hits, engineers face a chaotic, high-pressure environment. They must synthesize scattered logs, cryptic error screenshots, and constant noise in Slack—with virtually no time to think. The traditional diagnosis process is inherently slow, heavily manual, and exhausting. 

## 💡 The Solution

**SupportSight Live** acts as a real-time, highly intelligent Site Reliability Engineering (SRE) agent. It serves as an autonomous pair of hands and eyes that:
1. **Listens** to the engineer's voice as they describe the issue.
2. **Analyzes** live screenshots of the error or terminal.
3. **Parses** massive volumes of logs at high speed.
4. **Reasons** over all this data to provide grounded hypotheses.
5. **Guides or executes** safe diagnostic actions, governed by a strict human-in-the-loop confirmation step.

---

## 🧠 How SupportSight Uses Gemini 3.1 Flash Lite Preview

Unlike standard chat wrappers, SupportSight leverages the real-time, low-latency, and multimodal capabilities of the **Gemini Live API** (via `gemini-3.1-flash-lite-preview`). It maintains an active session where it concurrently processes three distinct streams of data:

- 🎙️ **Continuous Voice Input** — Engineers speak naturally, describing the incident verbally.
- 👁️ **Visual Context** — Real-time screen captures of terminals, IDEs, or dashboards.
- 📄 **High-Throughput Logs** — A custom Rust-powered parser processes logs at **1.2 GB/s**, extracting anomalies and feeding only the crucial, dense context to Gemini.

This multimodal reasoning enables **immediate, context-aware triage**. The agent understands what the engineer sees, hears, and is debugging, all simultaneously.

---

## ✨ Key Features

- **Voice Input:** Speak directly to the agent for hands-free diagnosis (utilizing the Web Speech API).
- **Screen Capture:** Share real-time screenshots of your terminal, IDE, or monitoring dashboards.
- **Ultra-Fast Log Analysis:** Paste large chunks of logs to be processed by a **SIMD-optimized Rust parser** that identifies root causes in `<10ms`.
- **Real-Time Anomaly Detection:** Identifies structural outliers and log corruption automatically.
- **Multimodal Reasoning:** Gemini fuses voice, vision, and text to generate high-confidence incident triage.
- **Hypothesis Engine:** Generates ranked hypotheses equipped with supporting evidence and probability scores.
- **Professional RAG:** Delivers grounded answers using **pgvector** for semantic search over official project runbooks.
- **Human-in-the-Loop Safety:** Implements a strict safety gate where no diagnostic or remediation action executes without explicit human approval.
- **Session Timeline:** Maintains a fully auditable trail of every event, observation, and decision made during the incident.

---

## 🏗️ Architecture & Tech Stack

SupportSight is designed as a robust, polyglot microservices architecture to maximize both performance and security:

```text
User (Voice + Screen + Logs)
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
│             Gemini 3.1 Flash Lite Preview            │
│              (Google GenAI SDK)              │
└──────────┬──────────────────────┬────────────┘
           │                      │
    ┌──────▼──────┐   ┌───────────▼──────────┐
    │ Logs Service│   │ Actions Service       │
    │ Rust + PyO3 │   │ Java 21 + Spring Boot │
    │ 1.2 GB/s    │   │ Allowlist + Audit Log │
    └─────────────┘   └───────────────────────┘
           │
    PostgreSQL 16 + Redis (Google Cloud SQL)
```

### Component Breakdown

| Component | Technology | Role & Description |
|-----------|-----------|-------------|
| **Backend Orchestrator** | Python 3.12, FastAPI, **Google GenAI SDK** | The brain of the operation. Orchestrates specialized sub-agents and handles streaming communication with the Gemini Live API. |
| **AI Model** | **Gemini 3.1 Flash Lite Preview** | Provides blazing-fast, multimodal, streaming reasoning to triage the incident. |
| **Log Parser Service** | **Rust** (Aho-Corasick) | Performs SIMD-optimized text parsing achieving 1.2 GB/s throughput. It acts as an anomaly detection filter so the AI only receives relevant errors. |
| **Actions Service** | **Java 17/21**, Spring Boot 3 | Executes shell/API actions safely. Ensures enterprise-grade security with strict allowlisting, dry-runs, and immutable auditing. |
| **Web Frontend** | **TypeScript**, Next.js 15 | A modern, responsive web client featuring real-time state updates and Lucide Icons. |
| **Mobile Frontend** | **Dart**, Flutter | A fully-featured cross-platform mobile client for iOS and Android on-the-go triage. |
| **Database** | PostgreSQL 16 + **pgvector**, Redis | Stores high-dimensional embeddings for runbooks (RAG) and low-latency session states. |
| **Infrastructure** | **Google Cloud Run**, Terraform | Fully serverless, scalable, and reproducible containerized deployment. |

> **Note for Judges:** The production architecture utilizes **Rust** for high-speed log parsing and **Java** for secure action execution. For ease of local evaluation without compiling Rust/Java, the `docker-compose.local.yml` configuration seamlessly injects a Python-based fallback.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- Java 21 (Maven)
- Rust (stable)
- Node.js 20+
- Flutter 3.22+ (for mobile app)
- Docker + Docker Compose
- A Gemini API key → [aistudio.google.com](https://aistudio.google.com)

### Option 1: Local Development (Docker Compose)

The easiest way to run the entire stack locally.

```bash
# 1. Clone the repo
git clone https://github.com/armandobecerraro/supportsight-live-agent.git
cd supportsight-live-agent

# 2. Set your Gemini API key
echo "GEMINI_API_KEY=your-key-here" > backend-orchestrator/.env

# 3. Start all services
docker-compose -f docker-compose.local.yml up --build

# 4. Open the web interface
open http://localhost:3000
```

### Option 2: Running Services Individually

Useful for active development on specific microservices.

```bash
# Backend Orchestrator (Port 8080)
cd backend-orchestrator
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080

# Logs Service (Python fallback — Port 8090)
cd logs-service
pip install fastapi uvicorn
uvicorn src.bridge.server:app --port 8090

# Actions Service (Port 8091)
cd actions-service
mvn spring-boot:run

# Web Frontend (Port 3000)
cd frontend
npm install && npm run dev
```

---

## 📱 Testing the Application

### Demo Scenarios
We provide three reproducible fixtures in [`docs/demo-fixtures/`](docs/demo-fixtures/):

| # | Scenario | Category |
|---|---------|---------|
| 1 | Payment API — 503 errors, DB connection pool exhausted | Database |
| 2 | Backend OOMKilled — memory leak, JVM heap | Backend |
| 3 | Deployment stuck — image pull 403 Forbidden | Deployment |

### Platform Testing
- **Run the Web App locally:** Use the in-app **Guide** for ready-to-run incident examples.
- **Run on iPhone/Android (Demo Video):** Use the Flutter app on a physical device or simulator. See [Run on iOS/Android](docs/flutter-ios-demo.md) for backend URL setup.
- **Automated Tests:** `pytest`, `cargo test`, `mvn test`, and `npm test` are configured for their respective services (with comprehensive test suites).

---

## ☁️ Deployment to Google Cloud Run

We use a bash script wrapping the Google Cloud SDK to deploy the microservices to Cloud Run concurrently.

```bash
export GCP_PROJECT_ID=your-project-id
export GCP_REGION=us-central1
export GEMINI_API_KEY=your-key
# ... set other secrets (DATABASE_URL, etc.)

chmod +x infra/cloudrun/deploy.sh
./infra/cloudrun/deploy.sh
```

See [`infra/cloudrun/`](infra/cloudrun/) for full deployment documentation.

---

## 📁 Project Structure

```text
supportsight-live-agent/
├── backend-orchestrator/     # Python + FastAPI + Gemini (Core logic & Agents)
├── logs-service/             # Rust log parser + Python FastAPI bridge
├── actions-service/          # Java 21 + Spring Boot 3 safe action executor
├── frontend/                 # Next.js 15 + TypeScript web client
├── flutter_app/              # Dart + Flutter cross-platform mobile client
├── docs/                     # Architecture diagrams, local runbooks, guides
├── infra/                    # Deployment scripts (Cloud Run) & Terraform
├── .github/workflows/        # CI/CD pipelines
└── docker-compose.local.yml  # Local environment setup
```

---

## 🛡️ Software Engineering Standards

We treated this project as a production-grade enterprise system:
- **SOLID Principles** & **Clean Architecture**: Domain logic is strictly separated from frameworks.
- **OWASP Top 10 2025**: API Key authentication, input validation, and secure headers.
- **12-Factor App**: Configuration strictly via environment variables; stateless services.
- **DevSecOps**: Automated CI pipelines test all 5 languages and run security scans on every push.
- **Observability-first**: Correlation IDs, structured JSON logging, and full session auditing.

---

## 🗺️ Roadmap — What's Built

These are the features we've already delivered:

- ✅ **pgvector** for full RAG over runbook documents
- ✅ **Anomaly Detection** in log streams
- ✅ **Enterprise Auditing** for actions
- ✅ **Voice Input** with Web Speech API
- ✅ **Screen Capture** for visual context
- ✅ **Rust-powered** log parser (1.2 GB/s)
- ✅ **Human-in-the-loop** safety gates
- ✅ **Google Cloud Run** deployment

---

## 📜 Devpost & License

🏆 **Submitted to the [Gemini Live Agent Challenge](https://geminiliveagentchallenge.devpost.com/)**  
Hashtag: **#GeminiLiveAgentChallenge**

- **Built with:** Gemini Live API (`gemini-3.1-flash-lite-preview`), Google GenAI SDK, Google Cloud Run
- **Languages:** Python, Rust, Java, TypeScript, Dart
- **Category:** UI Navigator / Live Agents

This project is licensed under the **MIT License** — See [LICENSE](LICENSE) for details.
