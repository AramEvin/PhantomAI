# PhantomAI — Step-by-Step Build Guide

## STEP 1: Get API Keys

### Required
- **Anthropic** → https://console.anthropic.com → Create API key → copy `ANTHROPIC_API_KEY`

### Optional (unlocks more tools)
- **Shodan** → https://account.shodan.io → My Account → API Key → `SHODAN_API_KEY`
- **VirusTotal** → https://www.virustotal.com/gui/my-apikey → `VIRUSTOTAL_API_KEY`

---

## STEP 2: Backend Setup

```bash
cd PhantomAI/backend

# Create virtual environment
python -m venv venv

# Activate
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run server
uvicorn app.main:app --reload --port 8000
```

✅ Backend running at: http://localhost:8000
✅ API docs at: http://localhost:8000/api/docs

---

## STEP 3: Frontend Setup

```bash
cd PhantomAI/frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# VITE_API_URL=http://localhost:8000 (default is fine)

# Run dev server
npm run dev
```

✅ Frontend running at: http://localhost:5173

---

## STEP 4: Test It

Open http://localhost:5173 and try:
- `8.8.8.8` (Google DNS)
- `1.1.1.1` (Cloudflare DNS)
- `github.com`
- `google.com`

---

## STEP 5: Docker (Production)

```bash
cd PhantomAI

# Copy and configure env
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Build and run everything
docker-compose up --build

# Access at http://localhost:5173
```

---

## Project Structure Explained

```
PhantomAI/
├── backend/
│   ├── app/
│   │   ├── main.py              ← FastAPI app creation, middleware, routes
│   │   ├── core/
│   │   │   └── config.py        ← All settings from .env
│   │   ├── models/
│   │   │   └── schemas.py       ← Pydantic request/response models
│   │   ├── api/routes/
│   │   │   ├── health.py        ← GET /api/health
│   │   │   └── investigate.py   ← POST /api/v1/investigate
│   │   ├── services/
│   │   │   ├── orchestrator.py  ← Runs all tools in parallel
│   │   │   ├── tools/
│   │   │   │   ├── base.py         ← Abstract base class for tools
│   │   │   │   ├── geoip.py        ← ip-api.com
│   │   │   │   ├── dns_lookup.py   ← dnspython
│   │   │   │   ├── whois_lookup.py ← python-whois
│   │   │   │   ├── ssl_cert.py     ← socket SSL + crt.sh
│   │   │   │   ├── subdomains.py   ← crt.sh certificate transparency
│   │   │   │   ├── http_headers.py ← httpx
│   │   │   │   ├── shodan_lookup.py ← Shodan API
│   │   │   │   ├── virustotal.py   ← VirusTotal API v3
│   │   │   │   └── blacklist.py    ← DNS-based blacklists
│   │   │   └── ai/
│   │   │       └── analyzer.py  ← Claude AI analysis
│   │   └── utils/
│   │       └── target.py        ← IP/domain helpers
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.tsx              ← Main layout
│       ├── store/
│       │   └── investigationStore.ts  ← Zustand state
│       └── components/
│           ├── layout/Header.tsx
│           ├── ui/SearchBar.tsx
│           ├── ui/HistoryPanel.tsx
│           └── tools/
│               ├── ResultsDashboard.tsx
│               ├── SummaryBar.tsx
│               ├── AIAnalysisCard.tsx
│               └── ToolCard.tsx
├── docker/
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── docker-compose.yml
└── docs/
    └── BUILD_GUIDE.md  ← You are here
```

---

## Adding New Tools

1. Create `backend/app/services/tools/mytool.py`
2. Extend `BaseTool`, implement `async def execute()`
3. Add to `ALL_TOOLS` list in `orchestrator.py`
4. Add icon/label in `frontend/src/components/tools/ToolCard.tsx`

That's it! The orchestrator handles parallelism and error handling automatically.
