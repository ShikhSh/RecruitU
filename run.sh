#!/usr/bin/env bash
# set -euo pipefail
# export $(grep -v '^#' .env | xargs -d '\n')
sudo apt install git -y
sudo apt update && sudo apt -y upgrade
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1:8b
ollama server


python3 -m venv .venv
source .venv/bin/activate
sudo apt install python3-pip
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080