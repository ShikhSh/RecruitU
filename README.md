# RecruitU

## Project Overview
RecruitU-LateralGPT is an application designed to facilitate recruitment processes through natural language search and AI-powered features to enhance networking efforts. The application includes intelligent caching mechanisms for improved performance and cost-effective LLM usage.

---

## File Structure

```
RecruitU/
├── backend_app/           # FastAPI backend application
│   ├── main.py            # FastAPI entry point with caching endpoints
│   ├── config.py          # Configuration settings
│   ├── clients.py         # Client classes for external services
│   ├── schemas.py         # Data schemas for validation and serialization
│   ├── nl_parser_llm.py   # Natural language parsing, LLM integration & caching
│   ├── similarity.py      # Similarity metrics functions
│   ├── utils.py           # Utility functions
│   ├── requirements.txt   # Python dependencies
│   ├── prompts/
│   │   └── nl_parser.json # LLM prompts configuration
│   ├── templates/
│   │   └── index.html     # Main HTML template
│   └── static/
│       └── styles.css     # CSS styles for the application
├── frontend_app/          # React frontend application
│   ├── src/
│   │   ├── App.tsx        # Main React component with caching
│   │   ├── components/    # React components
│   │   └── data/          # User data and types
│   └── package.json       # Node.js dependencies
├── .vscode/
│   └── launch.json        # VS Code debugging configuration
├── README.md              # Project documentation
└── run.sh                 # Shell script for environment setup
```

---

## Features

### Core Functionality
- **LateralGPT**: `/search_nl` converts natural language like `People at Tepper` into a structured search payload and returns results.
- **Pass‑through**: `/search` and `/people` forward to the official People API.
- **Conversation Suggestions**: When viewing a user, get LLM-powered suggestions for conversation starters based on common backgrounds.

### Performance & Caching
- **Query Parsing Cache**: TTL-based caching (2 hours) for LLM query parsing results to reduce API calls
- **Conversation Suggestions Cache**: TTL-based caching (1 hour) for conversation suggestions between user pairs
- **Frontend Caching**: Map-based caching in React for conversation suggestions per user pair

### API Endpoints
- `POST /cache/clear` - Clear specific or all caches
- `POST /search_nl` - Natural language search with caching
- `POST /suggest_conversation` - AI conversation suggestions with caching
- `GET /people` - User profile retrieval

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
pip install -r RecruitU-backend/requirements.txt
```

### Frontend Setup

```bash
cd RecruitU-frontend
sudo apt install npm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc && nvm install 16.20.2
source ~/.bashrc && nvm use 16.20.2
npm install react react-dom
npm install --save-dev typescript @types/react @types/react-dom
```

### Running the Application

#### Start frontend server (Terminal 1):
```bash
cd RecruitU-frontend
npm start 
```
The React app will run on [http://localhost:3000](http://localhost:3000).

For Production:
```bash
cd frontend_app
npm run build
npm install -g serve
serve -s build
```

#### Start backend server (Terminal 2):
```bash
source .venv/bin/activate
cd RecruitU-backend
uvicorn main:app --reload --port 8000 --host 0.0.0.0
```

The FastAPI backend will run on [http://localhost:8000](http://localhost:8000).

---

## Cache Management

### Cache Types
1. **Query Parsing Cache**: Stores LLM parsing results for natural language queries (TTL: 2 hours)
2. **Conversation Suggestions Cache**: Stores conversation suggestions between user pairs (TTL: 1 hour)

### Cache Endpoints
- `POST /cache/clear?cache_type=all` - Clear all caches
- `POST /cache/clear?cache_type=suggestions` - Clear only conversation suggestions cache
- `POST /cache/clear?cache_type=query_parsing` - Clear only query parsing cache

---

# Usage

- Access the backend at [http://localhost:8000](http://localhost:8000)
- Access the React UI at [http://localhost:3000](http://localhost:3000)
- Use the UI to:
  - Fetch a reference user by ID
  - Search for users using natural language (cached for performance)
  - Click a user to view details and get conversation suggestions (cached per user pair)

---


### Sample Queries Tested:
- someone who works in Parrish
- folks from Wharton
- graduates from Wharton
- students from wharton who graduated in 2007