#!/usr/bin/env bash
# set -euo pipefail
# export $(grep -v '^#' .env | xargs -d '\n')

sudo apt update && sudo apt -y upgrade
# Install Git:
sudo apt install git -y
# Check if installed
git --version
# Generate SSH key
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
# Add generated SSH key to Git

# Install Ollama:
curl -fsSL https://ollama.ai/install.sh | sh
# Pull the llama3.1:8b model
ollama pull llama3.1:8b

# Below is required on EC2 instances
sudo apt install python3.12-venv
# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Clone the repository
git clone https://github.com/ShikhSh/RecruitU.git

# Change to the project directory
cd RecruitU
# Install Python dependencies
sudo apt install python3-pip
pip install -r requirements.txt

sudo apt install npm
cd app/user-tile-ui
npm install react react-dom
npm install --save-dev typescript @types/react @types/react-dom
npm start
source ../.venv/bin/activate
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0

ollama serve
sudo systemctl stop ollama

## pytest==8.3.2
# pytest-asyncio==0.23.8