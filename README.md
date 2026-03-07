# PhantomAI 👁️ — OSINT Intelligence Platform

<div align="center">

![PhantomAI](https://img.shields.io/badge/PhantomAI-OSINT-7c3aed?style=for-the-badge&logo=ghost&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**AI-powered OSINT platform for IP and domain intelligence gathering.**  
Run 9 parallel reconnaissance tools and get a unified threat analysis from multiple AI providers.

[Features](#features) · [Architecture](#architecture) · [Installation](#installation) · [Configuration](#configuration) · [API Reference](#api-reference) · [File Structure](#file-structure)

</div>

---

## Overview

PhantomAI is a full-stack Open Source Intelligence (OSINT) platform that automates the process of investigating IP addresses and domains. It runs 9 intelligence-gathering tools concurrently and feeds the aggregated results to multiple AI providers simultaneously, producing a merged threat analysis report with risk scoring, infrastructure fingerprinting, and attack surface mapping.

---

## Features

### 🔧 OSINT Tools (run in parallel)
| Tool | Description |
|------|-------------|
| **GeoIP** | Geolocation, ISP, ASN lookup via ip-api.com |
| **DNS** | Full DNS record enumeration (A, AAAA, MX, NS, TXT, PTR, SOA) |
| **WHOIS** | Domain registration, registrar, expiry dates |
| **SSL/TLS** | Certificate details, SAN, validity, transparency logs |
| **Subdomains** | Subdomain enumeration via certificate transparency |
| **HTTP Headers** | Security header audit, server fingerprinting |
| **Shodan** | Port/service discovery, vulnerability data |
| **VirusTotal** | Malware detection, reputation scoring |
| **Blacklist** | DNSBL blacklist checks across 8 major providers |

### 🧠 Multi-AI Analysis Engine
Runs up to 7 AI providers **simultaneously** and merges results:
- **Anthropic Claude** — claude-sonnet-4-20250514
- **OpenAI GPT-4o**
- **Google Gemini** — gemini-2.0-flash
- **Groq** — llama-3.3-70b-versatile *(free, fast)*
- **Cohere** — command-a-03-2025
- **Mistral** — mistral-large-latest
- **Ollama** — local models (llama3, mistral, etc.)

### 📊 Analysis Output
- Risk level classification: `low` / `medium` / `high` / `critical`
- Risk score 0–100
- Infrastructure fingerprinting (hosting, CDN, cloud provider)
- Attack surface mapping (exposed services, entry points)
- Port & service risk assessment
- Threat intelligence (blacklist status, reputation, malware indicators)
- Key findings and remediation recommendations

### 🗄️ Scan History
- All scans persisted to PostgreSQL
- Browse, reload, and delete past scans
- Per-target scan statistics

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   React Frontend                     │
│         Vite + TypeScript + Zustand + Axios          │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP REST
┌─────────────────────▼───────────────────────────────┐
│                 FastAPI Backend                      │
│                                                     │
│  POST /api/v1/investigate                           │
│         │                                           │
│         ▼                                           │
│  InvestigationOrchestrator                          │
│         │                                           │
│    asyncio.gather()                                 │
│    ┌────┴────────────────────────────────┐          │
│    │  9 OSINT Tools run concurrently     │          │
│    └────┬────────────────────────────────┘          │
│         │                                           │
│    MultiAIAnalyzer                                  │
│    ┌────┴────────────────────────────────┐          │
│    │  7 AI providers run concurrently    │          │
│    │  Results merged into unified report │          │
│    └────┬────────────────────────────────┘          │
│         │                                           │
│    PostgreSQL (asyncpg + SQLAlchemy)                │
└─────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/PhantomAI.git
cd PhantomAI
```

### 2. Set up PostgreSQL
```bash
sudo apt install postgresql -y
sudo -u postgres psql -c "CREATE USER phantom WITH PASSWORD 'phantom';"
sudo -u postgres psql -c "CREATE DATABASE phantomdb OWNER phantom;"
```

### 3. Set up the backend
```bash
cd backend
pip install -r requirements.txt --break-system-packages
cp .env.example .env
# Edit .env with your API keys (see Configuration section)
```

### 4. Set up the frontend
```bash
cd frontend
npm install
cp .env.example .env
# Edit VITE_API_URL if needed
```

### 5. Start the services

**Backend:**
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd frontend
npm run dev -- --host 0.0.0.0
```

Open `http://localhost:5173` in your browser.

---

## Configuration

### Backend — `backend/.env`

```env
# ── Database ──────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://phantom:phantom@localhost:5432/phantomdb

# ── AI Providers (add keys for any you want to use) ───
ANTHROPIC_API_KEY=        # https://console.anthropic.com
OPENAI_API_KEY=           # https://platform.openai.com
GEMINI_API_KEY=           # https://aistudio.google.com (free)
GROQ_API_KEY=             # https://console.groq.com (free)
COHERE_API_KEY=           # https://cohere.com (free tier)
MISTRAL_API_KEY=          # https://console.mistral.ai

# ── Local AI (optional) ───────────────────────────────
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# ── OSINT Services (optional) ─────────────────────────
SHODAN_API_KEY=           # https://shodan.io (paid)
VIRUSTOTAL_API_KEY=       # https://virustotal.com (free tier)

# ── Server ────────────────────────────────────────────
ALLOWED_ORIGINS=http://localhost:5173,http://YOUR_SERVER_IP:5173
```

> **Minimum requirement:** At least one AI key. Groq is free and fast — recommended to start.

### Frontend — `frontend/.env`
```env
VITE_API_URL=http://localhost:8000
```

---

## File Structure

```
PhantomAI/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app, CORS, lifespan
│   │   ├── database.py                # SQLAlchemy async engine, ScanRecord model
│   │   ├── core/
│   │   │   └── config.py              # Pydantic settings, env parsing
│   │   ├── models/
│   │   │   └── schemas.py             # Pydantic request/response models
│   │   ├── api/routes/
│   │   │   ├── investigate.py         # POST /investigate, WS /ws/scan/{id}
│   │   │   ├── history.py             # GET/DELETE /history, GET /stats
│   │   │   └── health.py              # GET /health
│   │   ├── services/
│   │   │   ├── orchestrator.py        # Runs all tools + AI concurrently
│   │   │   ├── ws_manager.py          # WebSocket progress broadcaster
│   │   │   ├── ai/
│   │   │   │   └── analyzer.py        # Multi-AI engine + merge logic
│   │   │   └── tools/
│   │   │       ├── geoip.py           # ip-api.com geolocation
│   │   │       ├── dns_lookup.py      # dnspython full record lookup
│   │   │       ├── whois_lookup.py    # python-whois with timeout
│   │   │       ├── ssl_cert.py        # Live cert + crt.sh transparency
│   │   │       ├── subdomains.py      # crt.sh subdomain enumeration
│   │   │       ├── http_headers.py    # Security header audit
│   │   │       ├── shodan_lookup.py   # Shodan host lookup
│   │   │       ├── virustotal.py      # VirusTotal IP/domain reputation
│   │   │       └── blacklist.py       # DNSBL multi-list checker
│   │   └── utils/
│   │       └── target.py              # IP vs domain classifier
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    ├── src/
    │   ├── App.tsx                    # Root layout, routing logic
    │   ├── main.tsx                   # React entry point
    │   ├── store/
    │   │   └── investigationStore.ts  # Zustand state, API calls
    │   ├── components/
    │   │   ├── layout/
    │   │   │   └── Header.tsx         # Logo, title, tool badges
    │   │   ├── ui/
    │   │   │   ├── SearchBar.tsx      # Target input + investigate button
    │   │   │   └── HistoryPanel.tsx   # Sidebar scan history list
    │   │   └── tools/
    │   │       ├── ResultsDashboard.tsx   # Main results container
    │   │       ├── AIAnalysisCard.tsx     # Full AI report card
    │   │       ├── ToolCard.tsx           # Individual tool result card
    │   │       ├── SummaryBar.tsx         # Scan stats overview bar
    │   │       └── ScanProgress.tsx       # Loading animation
    │   └── styles/
    │       └── globals.css
    ├── index.html
    ├── package.json
    └── .env.example
```

---

## API Reference

### `POST /api/v1/investigate`
Run a full investigation on a target.

**Request:**
```json
{
  "target": "8.8.8.8"
}
```

**Response:**
```json
{
  "target": "8.8.8.8",
  "target_type": "ip",
  "timestamp": "2026-03-07T17:11:37Z",
  "duration_ms": 23140,
  "tools_run": 9,
  "tools_success": 9,
  "results": { ... },
  "ai_analysis": {
    "summary": "...",
    "risk_level": "low",
    "risk_score": 14,
    "key_findings": [...],
    "recommendations": [...],
    "infrastructure": { ... },
    "attack_surface": { ... },
    "port_risks": [...],
    "threat_intel": { ... }
  }
}
```

### `GET /api/v1/history`
Returns last 20 scans. Supports `?limit=`, `?offset=`, `?target=` query params.

### `GET /api/v1/history/{id}`
Returns full scan details including all tool results and AI analysis.

### `DELETE /api/v1/history/{id}`
Deletes a scan record.

### `GET /api/v1/stats`
Returns total scan count, breakdown by risk level, and top scanned targets.

### `GET /api/v1/health`
Health check. Returns `{"status": "ok"}`.

### `WebSocket /api/v1/ws/scan/{scan_id}`
Connect before POSTing to `/investigate` with the same `scan_id` to receive real-time tool progress events:
```json
{"event": "tool_start", "data": {"tool": "geoip"}}
{"event": "tool_done",  "data": {"tool": "geoip", "status": "success", "duration_ms": 312}}
{"event": "ai_start",   "data": {}}
{"event": "ai_done",    "data": {"risk_level": "low", "risk_score": 14}}
{"event": "scan_complete", "data": {"duration_ms": 23140}}
```

---

## Free API Keys

All of these have free tiers sufficient for personal use:

| Provider | URL | Notes |
|----------|-----|-------|
| Groq | https://console.groq.com | Free, fast, no credit card |
| Gemini | https://aistudio.google.com | Free tier, 15 req/min |
| Cohere | https://cohere.com | Free trial |
| Mistral | https://console.mistral.ai | Free trial |
| VirusTotal | https://virustotal.com | Free 500 req/day |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend framework | FastAPI + Uvicorn |
| Async runtime | Python asyncio |
| Database ORM | SQLAlchemy 2.0 async |
| Database driver | asyncpg |
| Database | PostgreSQL |
| AI SDK | anthropic, openai, google-genai, groq, cohere, mistralai |
| HTTP client | httpx, aiohttp |
| DNS | dnspython |
| WHOIS | python-whois |
| Frontend framework | React 18 + TypeScript |
| Build tool | Vite |
| State management | Zustand |
| HTTP client (FE) | axios |
| Styling | Inline styles (no CSS framework dependency) |

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">
Built with 👁️ by PhantomAI
</div>
