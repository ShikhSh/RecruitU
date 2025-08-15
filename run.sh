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
sudo apt install python3-pip
# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Clone the repository
git clone https://github.com/ShikhSh/RecruitU.git

# Change to the project directory
cd RecruitU

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd front-end-app
sudo apt install npm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc && nvm install 16.20.2
source ~/.bashrc && nvm use 16.20.2
npm install react react-dom
npm install --save-dev typescript @types/react @types/react-dom

# # Start frontend server
# npm start

# # Start backend server
# cd ../app
# uvicorn backend_app.main:app --reload --port 8000 --host 0.0.0.0

# # Start Ollama server
# # In a separate terminal, run:
# ollama serve

# # Stop Ollama server
# sudo systemctl stop ollama

## pytest==8.3.2
# pytest-asyncio==0.23.8