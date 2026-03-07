#!/bin/bash
# PhantomAI Quick Setup Script
set -e

echo "👻 PhantomAI Setup"
echo "=================="

# Backend
echo ""
echo "📦 Setting up backend..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
if [ ! -f .env ]; then
  cp .env.example .env
  echo "⚠️  Created backend/.env - please add your ANTHROPIC_API_KEY"
fi
cd ..

# Frontend
echo ""
echo "📦 Setting up frontend..."
cd frontend
npm install
if [ ! -f .env ]; then
  cp .env.example .env
fi
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit backend/.env and add your ANTHROPIC_API_KEY"
echo "  2. Run: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "  3. Run: cd frontend && npm run dev"
echo "  4. Open: http://localhost:5173"
