#!/bin/bash
# LifeLens AI — Setup Script (Mac/Linux)
set -e
GREEN='\033[0;32m'; BLUE='\033[0;34m'; NC='\033[0m'
echo -e "${BLUE}Setting up LifeLens AI...${NC}"
cd "$(dirname "$0")/../backend"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
touch database/__init__.py models/__init__.py routes/__init__.py utils/__init__.py
mkdir -p ml_models
echo -e "${GREEN}✅ Setup complete! Now run: bash scripts/run.sh${NC}"
