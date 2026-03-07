#!/bin/bash
trap 'kill %1 %2' SIGINT
cd backend && uvicorn main:app --reload --port 8000 &
cd frontend && npm run dev &
wait
