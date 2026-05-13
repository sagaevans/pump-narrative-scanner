# Pump Narrative Scanner

A local Python-based research dashboard for monitoring newly created Solana meme tokens and analyzing their narrative characteristics.

**This tool is for research and screening only. It does not provide investment advice and does not execute trades.**

## Features

- Monitor newly created Solana meme tokens
- Detect narrative patterns (meme, AI, political, animal, celebrity, etc.)
- Score tokens based on narrative strength
- Local SQLite storage for research data
- Simple web dashboard for viewing results

## Tech Stack

- Python
- FastAPI
- SQLite
- HTML / CSS / JavaScript

## Setup (Windows)

### Prerequisites

- Python 3.10 or higher installed ([python.org](https://www.python.org/downloads/))
- Git (optional, for cloning)

### Installation

1. **Clone the repository** (or download and extract the ZIP):

   ```bash
   git clone https://github.com/sagaevans/pump-narrative-scanner.git
   cd pump-narrative-scanner
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

   ```bash
   venv\Scripts\activate
   ```

4. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Create your environment file:**

   ```bash
   copy .env.example .env
   ```

   Edit `.env` if you want to change any default settings.

### Running the Dashboard

```bash
python main.py
```

The dashboard will be available at: **http://127.0.0.1:8000**

Press `Ctrl+C` in the terminal to stop the server.

## Project Structure

```
pump-narrative-scanner/
├── main.py                  # Entry point
├── config.py                # Configuration (loads from .env)
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── README.md                # This file
├── modules/
│   ├── __init__.py
│   ├── storage.py           # SQLite database operations
│   ├── narrative_detector.py # Narrative pattern detection
│   └── scoring.py           # Token scoring logic
├── web/
│   ├── __init__.py
│   ├── app.py               # FastAPI web application
│   ├── templates/
│   │   └── index.html       # Dashboard HTML template
│   └── static/
│       ├── style.css        # Dashboard styles
│       └── script.js        # Dashboard JavaScript
└── data/
    └── .gitkeep             # SQLite database stored here
```

## Disclaimer

This project is a research tool. It does not:
- Provide investment advice
- Execute trades or transactions
- Connect to any wallet
- Handle private keys
- Send alerts or notifications

Use at your own discretion for research purposes only.
