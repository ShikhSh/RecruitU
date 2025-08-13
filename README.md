# RecruitU

## Project Overview
RecruitU is an application designed to facilitate recruitment processes through various functionalities, including natural language processing and data similarity metrics.

## File Structure
recruitu-app/
├── app/
│   ├── main.py          # Entry point for the application
│   ├── config.py        # Configuration settings
│   ├── clients.py       # Client classes for external services
│   ├── schemas.py       # Data schemas for validation and serialization
│   ├── nl_parser.py     # Natural language processing functions
│   ├── similarity.py     # Similarity metrics functions
│   ├── utils.py         # Utility functions
│   ├── templates/
│   │   └── index.html   # Main HTML template
│   └── static/
│       └── styles.css   # CSS styles for the application
├── tests/
│   └── test_routes.py    # Unit tests for application routes
├── .env.example          # Template for environment variables
├── requirements.txt      # Python dependencies
├── Dockerfile            # Instructions for building Docker image
├── README.md             # Project documentation
└── run.sh                # Shell script for running the application

# RecruitU People API — LateralGPT + Doppelgänger (FastAPI/Python)

A tiny, production‑lean demo that turns **natural language** into RecruitU People API searches and computes **look‑alike (doppelgänger)** matches.

## Features
- **LateralGPT**: `/search_nl` converts text like `CMU '19 M&A at Evercore or Gugg in NYC` into a clean `/search` payload and returns results.
- **Pass‑through**: `/search` and `/people` forward to the official People API with your API key.
- **CSV Export**: `/export/csv?...` for quick list downloads.
- **Doppelgänger**: `/doppelganger?source_id=...` ranks similar profiles by education + experience.
- **Web UI**: index page to try NL search and view results.

## Getting Started

### 1) Configure
Create `.env` from example:
```bash
cp .env.example .env
# fill PEOPLE_API_BASE and PEOPLE_API_KEY



## Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   cd recruitu-app
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Copy `.env.example` to `.env` and fill in the required values.

5. Run the application:
   ```
   bash run.sh
   ```

## Usage
After running the application, navigate to `http://localhost:8000` in your web browser to access the RecruitU application.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.