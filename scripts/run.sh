#!/bin/bash
# LifeLens AI — Start Server (Mac/Linux)
cd "$(dirname "$0")/../backend"
[ -d "venv" ] && source venv/bin/activate
touch database/__init__.py models/__init__.py routes/__init__.py utils/__init__.py
mkdir -p ml_models
echo "🚀 Starting LifeLens AI..."
echo "🌐 Open browser: http://localhost:8000"
echo "📖 API Docs:     http://localhost:8000/api/docs"
python3 main.py
