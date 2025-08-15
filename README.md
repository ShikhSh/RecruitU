# RecruitU

## Project Overview
RecruitU-LateralGPT is an application designed to facilitate recruitment processes through natural language search and some AI powered features to enhance networking efforts.

---

## File Structure

```
recruitu-app/
├── app/
│   ├── main.py            # FastAPI entry point
│   ├── config.py          # Configuration settings
│   ├── clients.py         # Client classes for external services
│   ├── schemas.py         # Data schemas for validation and serialization
│   ├── nl_parser_llm.py   # Natural language parsing and LLM integration
│   ├── similarity.py      # Similarity metrics functions
│   ├── utils.py           # Utility functions
│   ├── templates/
│   │   └── index.html     # Main HTML template
│   └── static/
│       └── styles.css     # CSS styles for the application
├── font-end-app/          # React frontend (user-tile-ui)
│   ├── src/
│   └── ...                # React app source and config
├── tests/
│   └── test_routes.py     # Unit tests for application routes
├── .env.example           # Template for environment variables
├── requirements.txt       # Python dependencies
├── Dockerfile             # Instructions for building Docker image
├── README.md              # Project documentation
└── run.sh                 # Shell script for running the application
```

---

## Features

- **LateralGPT**: `/search_nl` converts natural language like `CMU '19 M&A at Evercore or Gugg in NYC` into a structured `/search` payload and returns results.
- **Pass‑through**: `/search` and `/people` forward to the official People API.
- **Conversation Suggestions**: When viewing a user, get LLM-powered suggestions for conversation starters based on common backgrounds with a reference user.

---

# Getting Started

## Setting up EC2 instance and installing dependencies:
### Update and upgrade
```bash
sudo apt update && sudo apt -y upgrade
```

### Install Git:
```bash
sudo apt install git -y
```

### Check if installed
```bash
git --version
```

### Generate SSH key
```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

### TODO: Add generated SSH key to your Git account

### Install Ollama:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Pull the llama3.1:8b model
```bash
ollama pull llama3.1:8b
```

### Below are required on EC2 instances
```bash
sudo apt install python3.12-venv
sudo apt install python3-pip
```

### Clone the repository
```bash
git clone https://github.com/ShikhSh/RecruitU.git
cd RecruitU
```

### Backend Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd front-end-app
sudo apt install npm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc && nvm install 16.20.2
source ~/.bashrc && nvm use 16.20.2
npm install react react-dom
npm install --save-dev typescript @types/react @types/react-dom
```

### In one terminal: Start frontend server
```bash
npm start
```
The React app will run on [http://localhost:3000](http://localhost:3000).

### In another terminal: Start backend server:
```bash
cd ../app
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
```

---

# Usage

- Access the backend at [http://localhost:8000](http://localhost:8000)
- Access the React UI at [http://localhost:3000](http://localhost:3000)
- Use the UI to:
  - Fetch a reference user by ID
  - Search for users using natural language
  - Click a user to view details and get conversation suggestions

---


### Sample Queries Tested:
- someone who works in Parrish
- folks from Wharton
- graduates from Wharton