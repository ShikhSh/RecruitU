#!/usr/bin/env bash
# set -euo pipefail
# export $(grep -v '^#' .env | xargs -d '\n')
sudo apt install git -y
sudo apt update && sudo apt -y upgrade
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1:8b
ollama serve

export OLLAMA_MODELS="/home/ubuntu/recruitu-app/RecruitU/models"
sudo systemctl stop ollama

python3 -m venv .venv
source .venv/bin/activate
sudo apt install python3-pip
pip install -r requirements.txt

sudo apt install npm
cd app/user-tile-ui
npm install react react-dom
npm install --save-dev typescript @types/react @types/react-dom
npm start
source ../.venv/bin/activate
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0