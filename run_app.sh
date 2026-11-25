#!/usr/bin/env bash
# SkillBridge: Production Startup Script
# Boots FastAPI Core Engine and Classy React Frontend

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "=========================================================="
echo "SkillBridge: Career Path & Skill-Gap Analyzer"
echo "=========================================================="

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "../.venv" ]; then
    source ../.venv/bin/activate
fi

# Ensure frontend is built for single-command zero-dependency serving
if [ ! -d "frontend/dist" ]; then
    echo "Building React frontend..."
    (cd frontend && npm install && npm run build)
fi

echo "Starting SkillBridge Server on http://localhost:8000"
echo "   - Web App UI:    http://localhost:8000"
echo "   - REST API Docs: http://localhost:8000/docs"
echo "=========================================================="

python -m uvicorn src.api:app --host 127.0.0.1 --port 8000
