# 👻 PhantomAI — Project Structure

```
PhantomAI/
│
├── 📄 .env.example               # Environment variables template
├── 📄 .gitignore
├── 📄 README.md
├── 📄 docker-compose.yml         # Run full stack with one command
│
├── 🐍 backend/
│   ├── main.py                   # FastAPI app entry, CORS, middleware
│   ├── requirements.txt
│   ├── Dockerfile
│   │
│   ├── core/                     # Infrastructure layer
│   │   ├── config.py             # Pydantic settings, loads .env
│   │   ├── logger.py             # Structured logging
│   │   ├── rate_limiter.py       # Per-IP rate limiting middleware
│   │   ├── exceptions.py         # Custom exceptions + global handlers
│   │   └── validators.py         # IP/domain input validation
│   │
│   ├── models/                   # Pydantic schemas
│   │   ├── request.py            # ScanRequest, ToolRequest
│   │   └── response.py           # ToolResult, ScanResponse, AIAnalysis
│   │
│   ├── tools/                    # Recon tools — each extends BaseTool
│   │   ├── base.py               # Abstract BaseTool interface
│   │   ├── whois_tool.py         # WHOIS lookup
│   │   ├── dns_tool.py           # DNS records (A/MX/NS/TXT/CNAME)
│   │   ├── geo_tool.py           # Geolocation via ip-api.com
│   │   ├── port_tool.py          # Async port scanner
│   │   ├── ssl_tool.py           # SSL/TLS certificate inspector
│   │   ├── subdomain_tool.py     # Subdomain discovery via crt.sh
│   │   ├── reputation_tool.py    # Blacklists + AbuseIPDB + VirusTotal
│   │   ├── headers_tool.py       # HTTP headers + tech fingerprint
│   │   ├── shodan_tool.py        # Shodan API (optional, paid)
│   │   └── registry.py           # tool_id → class mapping
│   │
│   ├── routers/                  # API route handlers
│   │   ├── scan.py               # POST /api/scan — run all tools
│   │   ├── tools.py              # GET/POST /api/tools
│   │   ├── ai.py                 # POST /api/ai/analyze + SSE stream
│   │   └── health.py             # GET /health
│   │
│   └── ai/                       # Claude AI integration
│       ├── analyst.py            # Builds prompt, calls Anthropic API
│       ├── prompts.py            # System + analysis prompt templates
│       └── streaming.py          # SSE streaming for real-time AI output
│
├── ⚛️  frontend/
│   ├── index.html                # HTML shell, loads fonts
│   ├── package.json
│   ├── vite.config.js            # Vite + /api proxy → backend
│   ├── tailwind.config.js        # Custom dark theme tokens
│   ├── Dockerfile
│   │
│   └── src/
│       ├── main.jsx              # React entry point
│       ├── App.jsx               # Root component + routing
│       │
│       ├── pages/
│       │   ├── Home.jsx          # Main scan page
│       │   └── Report.jsx        # Full report detail view
│       │
│       ├── components/
│       │   ├── Header.jsx        # Logo + nav bar
│       │   ├── ScanInput.jsx     # Target input + SCAN button
│       │   ├── ToolSelector.jsx  # Module toggle grid
│       │   ├── ProgressBar.jsx   # Animated scan progress
│       │   ├── ResultsGrid.jsx   # Live results grid
│       │   ├── ToolCard.jsx      # Individual result card
│       │   ├── AISummary.jsx     # Claude analysis + SSE stream
│       │   ├── JsonViewer.jsx    # Syntax-highlighted JSON tree
│       │   ├── ScanHistory.jsx   # Recent scans list
│       │   └── StatusDot.jsx     # Animated status indicator
│       │
│       ├── hooks/
│       │   ├── useScan.js        # Core scan orchestration hook
│       │   ├── useSSE.js         # Server-Sent Events hook
│       │   └── useScanHistory.js # localStorage scan history
│       │
│       ├── utils/
│       │   ├── api.js            # Axios instance + typed helpers
│       │   ├── validators.js     # Client-side IP/domain validation
│       │   └── formatters.js     # Date, port, risk color formatters
│       │
│       └── styles/
│           ├── globals.css       # Tailwind directives + animations
│           └── theme.js          # Design tokens (colors, fonts)
│
├── 🔗 shared/
│   ├── constants.js              # TOOL_IDS, RISK_LEVELS, STATUS_TYPES
│   └── tool-definitions.json     # Tool metadata (id, label, icon, desc)
│
├── 📚 docs/
│   ├── architecture.md           # System diagram + data flow
│   ├── api-reference.md          # All endpoints + schemas + examples
│   └── adding-tools.md           # Guide to adding new recon tools
│
├── 🛠️  scripts/
│   ├── setup.sh                  # One-command install (deps + .env)
│   └── dev.sh                    # Start backend + frontend in parallel
│
└── 🧪 tests/
    ├── backend/
    │   ├── test_tools.py         # Unit tests per tool (mocked network)
    │   └── test_api.py           # Integration tests (FastAPI TestClient)
    └── frontend/
        └── ScanInput.test.jsx    # Component tests (Vitest)
```

## Data Flow

```
User enters IP/Domain
        │
        ▼
  [Frontend] ScanInput
        │ POST /api/scan
        ▼
  [Backend] routers/scan.py
        │ asyncio.gather()
        ▼
  [Tools] whois + dns + geo + ports + ssl + ...  ← run in parallel
        │
        ▼
  [Backend] routers/ai.py
        │ Anthropic Claude API
        ▼
  [AI] analyst.py → threat analysis
        │ SSE stream
        ▼
  [Frontend] AISummary.jsx ← real-time typewriter output
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/scan | Run selected tools on target |
| GET | /api/tools | List all available tools |
| POST | /api/tools/{id} | Run single tool |
| POST | /api/ai/analyze | Get AI threat analysis |
| GET | /api/ai/stream | SSE stream of AI analysis |
| GET | /health | Service health check |
