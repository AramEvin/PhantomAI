# 👻 PhantomAI — OSINT Intelligence Tool

PhantomAI is an AI-powered OSINT tool that investigates IP addresses and domains.

## Architecture
```
PhantomAI/
├── backend/          # Python FastAPI
│   └── app/
│       ├── api/routes/    # REST endpoints
│       ├── core/          # Config, settings
│       ├── models/        # Pydantic schemas
│       ├── services/
│       │   ├── tools/     # 10+ OSINT tools
│       │   └── ai/        # Claude AI integration
│       └── utils/
├── frontend/         # React + Vite + Tailwind
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── hooks/
│       └── store/         # Zustand state
├── docker/
├── docs/
└── scripts/
```
