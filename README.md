# PhantomAI 👁️ — OSINT Intelligence Platform

<div align="center">

![PhantomAI](https://img.shields.io/badge/PhantomAI-OSINT-7c3aed?style=for-the-badge&logo=ghost&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.118-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**AI-powered OSINT platform for IP and domain intelligence gathering.**  
Run **15 parallel reconnaissance tools** and get a unified threat analysis from up to **11 AI providers simultaneously.**

[Features](#features) · [Tools](#osint-tools) · [AI Providers](#ai-providers) · [Installation](#installation) · [Configuration](#configuration) · [API](#api-reference) · [Structure](#file-structure)

</div>

---

## Features

- 🔍 **15 OSINT tools** running in parallel — GeoIP, DNS, WHOIS, SSL, Subdomains, HTTP Headers, Shodan, VirusTotal, Blacklist, **Nmap**, **CVE Lookup**, **Reverse IP**, **WHOIS History**, **Leak/Breach Check**, **BGP/ASN Intel**
- 🧠 **11 AI providers** analyzed simultaneously — Claude, GPT-4o, Gemini, Groq, Cohere, Mistral, DeepSeek, Grok, Perplexity, Together, Ollama
- 🛡 **CVE findings** with CVSS scores pulled live from NVD (National Vulnerability Database)
- 💧 **Breach detection** via HaveIBeenPwned API
- 🌐 **BGP/ASN routing intelligence** — netblock owner, upstreams, IP prefixes
- 🔬 **Real Nmap scans** — port detection, OS fingerprinting, service version banners
- 🔄 **Reverse IP** — all domains co-hosted on the same IP
- 📅 **WHOIS History** — ownership change tracking
- 🗺 **Interactive map** — target geolocation on dark CartoDB tiles
- 📊 **Severity-tagged findings** (Critical / Medium / OK) with step-by-step remediation
- 🗄 **Scan history** persisted in PostgreSQL
- 🐳 **Docker Compose** — one command deployment

---

## OSINT Tools

| Tool | Description | API Key Required |
|------|-------------|-----------------|
| GeoIP | Geolocation, ISP, ASN, coordinates | No |
| DNS Lookup | A, MX, NS, TXT, CNAME records | No |
| WHOIS | Registrar, registrant, dates | No |
| SSL/TLS | Certificate details, expiry, issuer, SANs | No |
| Subdomains | Passive subdomain enumeration | No |
| HTTP Headers | Security headers audit, server info | No |
| Shodan | Open ports, CVEs, banners from Shodan index | `SHODAN_API_KEY` |
| VirusTotal | Malware, reputation, detections | `VIRUSTOTAL_API_KEY` |
| Blacklist | DNS blacklist/RBL check | No |
| **Nmap** | Real port scan, OS detection, service versions | No (nmap binary) |
| **CVE Lookup** | Live CVE search via NVD API by detected software | Optional: `NVD_API_KEY` |
| **Reverse IP** | All domains hosted on same IP via HackerTarget | No |
| **WHOIS History** | Domain ownership changes over time | Optional: `WHOISXML_API_KEY` / `SECURITYTRAILS_API_KEY` |
| **Leak / Breach** | HaveIBeenPwned domain breach + paste check | `HIBP_API_KEY` |
| **BGP / ASN** | Routing info, netblock, upstream providers via BGPView | No |

---

## AI Providers

| Provider | Model | Key |
|----------|-------|-----|
| Anthropic Claude | claude-sonnet-4-20250514 | `ANTHROPIC_API_KEY` |
| OpenAI | gpt-4o | `OPENAI_API_KEY` |
| Google Gemini | gemini-2.0-flash | `GEMINI_API_KEY` |
| Groq | llama-3.3-70b-versatile | `GROQ_API_KEY` |
| Cohere | command-a-03-2025 | `COHERE_API_KEY` |
| Mistral | mistral-large-latest | `MISTRAL_API_KEY` |
| DeepSeek | deepseek-chat | `DEEPSEEK_API_KEY` |
| xAI Grok | grok-3 | `GROK_API_KEY` |
| Perplexity | sonar (live web search) | `PERPLEXITY_API_KEY` |
| Together AI | Llama-3.3-70B-Instruct-Turbo | `TOGETHER_API_KEY` |
| Ollama | llama3 (local) | None (self-hosted) |

At least one AI key is required for analysis. All configured providers run in parallel and results are merged.

---

## Installation

### Prerequisites

- Docker + Docker Compose
- At least one AI API key

### Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/youruser/PhantomAI.git
cd PhantomAI

# 2. Create environment file
cp docker.env.example .env

# 3. Edit .env — add your API keys and set your server IP
nano .env

# 4. Build and start all containers
docker compose up --build -d

# 5. Check everything is running
docker compose ps
docker compose logs -f backend
```

Frontend: `http://YOUR_SERVER_IP:3000`  
Backend API: `http://YOUR_SERVER_IP:8000/api/v1/health`

---

## Configuration

### `.env` file (root of project)

```bash
# ── Server ────────────────────────────────────────────
VITE_API_URL=http://YOUR_SERVER_IP:8000       # ← REQUIRED: set to your actual IP
ALLOWED_ORIGINS=http://YOUR_SERVER_IP:3000

# ── Database ──────────────────────────────────────────
# (handled automatically by docker-compose)

# ── AI Providers (add at least one) ───────────────────
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GEMINI_API_KEY=
GROQ_API_KEY=
COHERE_API_KEY=
MISTRAL_API_KEY=
DEEPSEEK_API_KEY=
GROK_API_KEY=
PERPLEXITY_API_KEY=
TOGETHER_API_KEY=

# ── OSINT Tools ───────────────────────────────────────
SHODAN_API_KEY=           # https://shodan.io
VIRUSTOTAL_API_KEY=       # https://virustotal.com (500 free/day)

# ── New Tools (all optional, degrade gracefully) ──────
NVD_API_KEY=              # https://nvd.nist.gov/developers/request-an-api-key (free, raises rate limit)
HIBP_API_KEY=             # https://haveibeenpwned.com/API/Key (~$4/month)
WHOISXML_API_KEY=         # https://whoisxmlapi.com (500 free/month)
SECURITYTRAILS_API_KEY=   # https://securitytrails.com (50 free/month)
```

> **Important:** After editing `.env`, rebuild the frontend — `VITE_API_URL` is baked into the JS bundle at build time:
> ```bash
> docker compose down && docker compose up --build -d
> ```

---

## Docker Commands

```bash
# Start everything
docker compose up -d

# Full rebuild (after code or .env changes)
docker compose down && docker compose up --build -d

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Check container status
docker compose ps

# Stop everything
docker compose down

# Stop and wipe database volume
docker compose down -v
```

---

## API Reference

### POST `/api/v1/investigate`

Run a full investigation on an IP or domain.

```bash
curl -X POST http://localhost:8000/api/v1/investigate \
  -H "Content-Type: application/json" \
  -d '{"target": "8.8.8.8"}'
```

**Request body:**
```json
{
  "target": "example.com",
  "tools": null        // null = run all 15 tools; or pass a list to filter
}
```

**Response:** Full `InvestigationResult` with all tool results + AI analysis.

---

### GET `/api/v1/history`

```bash
curl http://localhost:8000/api/v1/history?limit=20
```

### GET `/api/v1/history/{id}`

Full result of a past scan.

### DELETE `/api/v1/history/{id}`

Delete a scan record.

### GET `/api/v1/stats`

Scan statistics — total scans, risk level distribution, top targets.

### GET `/api/v1/health`

Health check — returns `{"status": "ok"}`.

---

## File Structure

```
PhantomAI/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app, lifespan, CORS
│   │   ├── core/
│   │   │   └── config.py              # All settings + API keys via pydantic-settings
│   │   ├── models/
│   │   │   └── schemas.py             # Pydantic models (TargetType, AIAnalysis, CVEFinding…)
│   │   ├── database.py                # SQLAlchemy async engine + ScanRecord model
│   │   ├── utils/
│   │   │   └── target.py              # classify_target(), resolve_to_ip(), TargetType
│   │   ├── api/routes/
│   │   │   ├── investigate.py         # POST /investigate
│   │   │   ├── history.py             # GET/DELETE /history, GET /stats
│   │   │   └── health.py              # GET /health
│   │   └── services/
│   │       ├── orchestrator.py        # Runs all 15 tools in parallel
│   │       ├── ai/
│   │       │   └── analyzer.py        # Multi-AI engine (11 providers)
│   │       └── tools/
│   │           ├── geoip.py
│   │           ├── dns_lookup.py
│   │           ├── whois_lookup.py
│   │           ├── ssl_cert.py
│   │           ├── subdomains.py
│   │           ├── http_headers.py
│   │           ├── shodan_lookup.py
│   │           ├── virustotal.py
│   │           ├── blacklist.py
│   │           ├── nmap_scan.py       # ← NEW
│   │           ├── cve_lookup.py      # ← NEW (NVD API)
│   │           ├── reverse_ip.py      # ← NEW (HackerTarget)
│   │           ├── whois_history.py   # ← NEW (WhoisXML / SecurityTrails)
│   │           ├── leakdb.py          # ← NEW (HaveIBeenPwned)
│   │           └── bgp_asn.py         # ← NEW (BGPView)
│   ├── Dockerfile                     # Includes nmap binary
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── store/
│   │   │   └── investigationStore.ts  # Zustand store
│   │   └── components/
│   │       ├── layout/Header.tsx
│   │       ├── ui/SearchBar.tsx
│   │       ├── ui/HistoryPanel.tsx
│   │       └── tools/
│   │           ├── ResultsDashboard.tsx
│   │           ├── AIAnalysisCard.tsx  # 6 tabs: Findings, CVEs, Infra, Attack, Ports, Threat
│   │           ├── ToolCard.tsx
│   │           ├── SummaryBar.tsx
│   │           ├── ScanProgress.tsx
│   │           └── TargetMap.tsx       # Leaflet dark map
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── .env                               # ← Edit this before running
├── .gitignore
├── .pre-commit-config.yaml
└── README.md
```

---

## Security Notes

- All API keys are loaded from environment variables — never hardcoded
- `detect-secrets` pre-commit hook prevents accidental key commits
- GitHub Actions CI runs secret scanning on every push
- Nmap requires the container to run with sufficient privileges for OS detection — if OS detection fails, port/service scanning still works
- HIBP breach data is read-only — PhantomAI only queries, never submits data

---

## License

MIT — see [LICENSE](LICENSE)
