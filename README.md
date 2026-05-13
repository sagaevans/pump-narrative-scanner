# Pump Narrative Scanner

A local Python-based research dashboard for monitoring newly created Solana meme tokens and analyzing their narrative characteristics. The app fetches public token metadata, classifies narratives using keyword detection, scores tokens across multiple research dimensions, and displays results in a local web dashboard.

---

## Important Disclaimer

**This tool is for research and screening purposes only.**

- This is NOT financial advice.
- This does NOT execute trades or transactions.
- This does NOT connect to any wallet.
- This does NOT handle private keys.
- This is NOT an auto-trading bot or sniper bot.
- This is NOT a Telegram bot or alert system.
- This does NOT run as a hosted website or GitHub Pages site.

GitHub is used only as the source code repository. The application runs locally on your machine.

---

## Features (Currently Implemented)

- **Live Token Fetching** — Pulls newly created token metadata from pump.fun's public API (read-only, no authentication required)
- **Automatic Fallback** — If the live API is unavailable (timeout, error, offline), the app falls back to built-in sample data so the dashboard always works locally
- **Narrative Detection** — Classifies tokens into 11 narrative categories using keyword matching against token name, symbol, and description
- **Multi-Factor Scoring Engine** — Scores each token across 6 dimensions with a weighted final score
- **Risk Level Assessment** — Assigns low/medium/high risk based on pump-like signals and safety indicators
- **SQLite Storage** — Persists all scored token data locally in a file-based database
- **Web Dashboard** — Dark-themed responsive dashboard with token cards, scores, and filters
- **Dashboard Filters** — Search by name/symbol, filter by minimum score, filter by risk level
- **Single-Command Startup** — One command starts everything: database, data fetch, scoring, and web server

---

## Narrative Categories

The detector classifies tokens into these categories (checked in priority order):

| Category | Description |
|----------|-------------|
| `disease_virus` | Virus/disease-themed tokens |
| `lockdown_pandemic` | Pandemic/lockdown narratives |
| `war` | Military/conflict themes |
| `breaking_news` | Urgency/breaking news framing |
| `finance_panic` | Market crash/bank run themes |
| `politics` | Political figures/movements |
| `ai` | AI/tech narratives |
| `celebrity` | Celebrity-branded tokens |
| `animal_meme` | Animal memes (doge, cat, frog) |
| `absurd_meme` | Internet culture memes |
| `unknown` | No recognized pattern |

High-risk categories (commonly associated with pump schemes): `disease_virus`, `lockdown_pandemic`, `war`, `breaking_news`, `finance_panic`.

---

## Scoring System

Each token receives 6 individual scores (0.0 to 1.0) plus a weighted final score:

| Score | Weight | What It Measures |
|-------|--------|-----------------|
| Narrative Score | 30% | Strength of detected narrative pattern |
| Momentum Score | 25% | Viral/trending potential based on metadata |
| Safety Score | 20% | Legitimacy indicators (website, social, effort) |
| Social Score | 15% | Social media presence (Twitter, Telegram, website) |
| Freshness Score | 10% | Timeliness and recency signals |

**Final Score Formula:**
```
Final Score = Narrative × 0.30 + Momentum × 0.25 + Social × 0.15 + Safety × 0.20 + Freshness × 0.10
```

**Additional metric:**
- **Hantavirus-like Score** — Measures how closely a token resembles known pump-and-dump patterns (not included in final score, used for risk level determination)

**Risk Levels:**
- **High** — Hantavirus-like score >= 0.6 OR Safety score <= 0.3
- **Medium** — Hantavirus-like score >= 0.35 OR Safety score <= 0.5
- **Low** — All other cases

---

## Project Structure

```
pump-narrative-scanner/
├── main.py                     # Entry point (init DB, fetch, score, serve)
├── config.py                   # Configuration loader (reads .env)
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── README.md                   # This file
├── modules/
│   ├── __init__.py
│   ├── pump_client.py          # Token data fetcher (pump.fun public API + fallback)
│   ├── narrative_detector.py   # Keyword-based narrative classification
│   ├── scoring.py              # Multi-factor scoring engine
│   └── storage.py              # SQLite database operations
├── web/
│   ├── __init__.py
│   ├── app.py                  # FastAPI web application + API endpoints
│   ├── templates/
│   │   └── index.html          # Dashboard HTML template
│   └── static/
│       ├── style.css           # Dark-theme responsive CSS
│       └── script.js           # Client-side filtering and rendering
└── data/
    └── .gitkeep                # SQLite database stored here at runtime
```

---

## Setup (Windows)

### Prerequisites

- Python 3.10 or higher ([download from python.org](https://www.python.org/downloads/))
- Git (optional, for cloning)

### Installation

1. **Clone the repository:**

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

   You can edit `.env` to change settings, or leave defaults as-is.

---

## Running the Application

### Start the Scanner and Dashboard

```bash
python main.py
```

This single command does everything:
1. Initializes the SQLite database (`data/coins.db`)
2. Attempts to fetch live token data from pump.fun public API
3. Falls back to built-in sample data if the API is unreachable
4. Runs each token through the narrative detector and scoring engine
5. Saves scored results to the database
6. Starts the FastAPI web server

### Access the Dashboard

Open your browser and go to:

```
http://127.0.0.1:8000
```

Press `Ctrl+C` in the terminal to stop the server.

---

## Dashboard Usage

The dashboard displays token cards with:
- Token name and symbol
- Risk level badge (color-coded: red = high, orange = medium, green = low)
- Narrative category badge (color-coded by type)
- All score values (narrative, hantavirus-like, momentum, social, safety, freshness, final)
- Mint address
- Analysis reason text
- "Open Token" button linking to the token's pump.fun page

### Filters

- **Search** — Type a name or symbol to filter tokens (case-insensitive partial match)
- **Min Score** — Set a minimum final score threshold (0.0 to 1.0)
- **Risk Level** — Filter by Low, Medium, or High

Click **Apply** to filter, or **Clear** to reset.

---

## How the Database Works

- The database is a SQLite file stored at `data/coins.db`
- It is created automatically on first run
- Tokens are stored with a unique constraint on `mint_address` (INSERT OR REPLACE)
- If the database already contains tokens, the startup fetch is skipped
- To re-fetch fresh data, delete `data/coins.db` and restart the app:

  ```bash
  del data\coins.db
  python main.py
  ```

### Database Schema

The `tokens` table contains 22 columns:
- Metadata: `id`, `name`, `symbol`, `mint_address`, `description`, `image_url`, `website`, `twitter`, `telegram`, `pump_url`
- Scores: `narrative_category`, `narrative_score`, `hantavirus_like_score`, `momentum_score`, `social_score`, `safety_score`, `freshness_score`, `final_score`
- Assessment: `risk_level`, `reason`
- Timestamps: `created_at`, `scanned_at`

---

## How the Fallback Works

The pump client (`modules/pump_client.py`) attempts to fetch live data from pump.fun's public API. If the request fails for any reason, the app gracefully falls back to 7 built-in sample tokens:

**Fallback triggers:**
- API request timeout (15 seconds)
- Connection error or network unavailable
- Non-200 HTTP status code
- Empty or malformed API response

**Result:** The dashboard always works, whether or not you have an internet connection. Sample data covers diverse narrative categories for testing the scoring system.

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard HTML page |
| `/api/health` | GET | Health check (`{"status": "ok"}`) |
| `/api/tokens` | GET | Token data with optional filters |

### `/api/tokens` Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Filter by name or symbol (partial, case-insensitive) |
| `min_score` | float | Minimum final score (0.0 to 1.0) |
| `risk_level` | string | Filter: `low`, `medium`, or `high` |
| `limit` | int | Max results to return (default: 100) |

---

## Environment Variables

Configured via `.env` file (copy from `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_HOST` | `127.0.0.1` | Host address for the web server |
| `APP_PORT` | `8000` | Port for the web server |
| `DATABASE_PATH` | `data/coins.db` | Path to SQLite database file |
| `SCAN_INTERVAL_SECONDS` | `60` | Scan interval (reserved for future use) |
| `PUMP_API_URL` | `https://frontend-api-v2.pump.fun/coins/latest` | Public API endpoint |
| `PUMP_API_TIMEOUT` | `15` | API request timeout in seconds |
| `PUMP_FETCH_LIMIT` | `20` | Number of tokens to fetch per request |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.10+, FastAPI 0.115.0 |
| Web Server | Uvicorn 0.30.6 |
| Templating | Jinja2 3.1.4 |
| HTTP Client | aiohttp 3.10.5 |
| Configuration | python-dotenv 1.0.1 |
| Database | SQLite (built-in, no install needed) |
| Frontend | HTML, CSS, vanilla JavaScript |

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'fastapi'"
Make sure you activated the virtual environment and installed dependencies:
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### Dashboard shows no tokens
The database may already exist with stale data. Delete it and restart:
```bash
del data\coins.db
python main.py
```

### "Connection error" or "API returned status 503"
This is expected if the pump.fun API is down or you're offline. The app automatically uses fallback sample data. The dashboard will still work.

### Port 8000 already in use
Another process is using port 8000. Either stop it, or change the port in your `.env` file:
```
APP_PORT=8080
```

### Python not recognized
Make sure Python 3.10+ is installed and added to your PATH. Try:
```bash
python --version
```
If that doesn't work, try `python3 --version` or reinstall Python with "Add to PATH" checked.

---

## Future Roadmap

Potential future enhancements (not yet implemented):
- Periodic background scanning (auto-refresh on interval)
- Real-time WebSocket token stream
- Historical token data and trend charts
- Export to CSV
- Advanced scoring with on-chain data (holder count, liquidity)
- Configurable keyword lists for narrative detection
- Token deduplication and update tracking

---

## Important: How This Project Works

- **GitHub** is used only as the source code repository for version control and collaboration
- **This is NOT a static GitHub Pages website** — there is no hosted version
- **The app runs locally** on your Windows (or Mac/Linux) machine
- **You must run `python main.py`** in a terminal to start the scanner and dashboard
- **The dashboard is accessed at `http://127.0.0.1:8000`** in your local browser
- **No deployment, hosting, or cloud infrastructure is required**
