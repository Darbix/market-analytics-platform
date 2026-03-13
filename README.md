# Market Analytics Platform

A lightweight full-stack web application for cryptocurrency market analysis.

The platform retrieves market data from the [Binance](https://www.binance.com/en/binance-api) REST API, performs asynchronous computations of technical indicators and statistical simulations, and visualizes results through an interactive web interface.

This project is currently a work in progress and serves as a personal project to explore modern backend architecture, background processing, and data-driven visualization.


## Features

- Cryptocurrency price history retrieval
- Technical indicator computation (e.g., RSI, volatility)
- Monte Carlo price simulation
- Asynchronous background jobs using Celery
- REST API built with FastAPI
- Interactive charts using React and Chart.js
- PostgreSQL storage for historical data
- CLI tool

## Project Structure

```bash
.
├── app/
├── backend/
│   └── app/
│   │   ├── api/          # FastAPI routes and Pydantic schemas
│   │   ├── core/         # Configuration (env vars) and database setup
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── services/     # Market data processing and business logic
│   │   └── workers/      # Celery background tasks and async processing
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/             # Frontend React web application
├── cli/                  # CLI
│   ├── cli_tool/         # Python package for CLI logic and API wrappers
│   └── pyproject.toml
├── docker-compose.yml
└── README.md
```


## Project Setup

### 1. Clone the repository

```bash
git clone https://github.com/darbix/market-analytics-platform.git
cd market-analytics-platform
```

### 2. Configure environment variables
```
cp .env.example .env
```

### 3. Start backend services
```
docker compose up --build
```
This starts:

- FastAPI backend
- Celery worker
- PostgreSQL
- Redis

API will be available at:
```
http://localhost:8000
```

### 4. Run the frontend
```
npm install --prefix frontend
npm run dev --prefix frontend -- --host
```

### 5. Install CLI dependencies
```
poetry install -C cli/
```


## Command Line Interface (CLI)
Activate the environment:
```
poetry shell -C cli/
```

General help:
```
market-cli --help
```

Example commands:
```
market-cli analyze BTCUSDT --interval 1d --limit 30 --monte-carlo-runs 500
market-cli download ETHUSDT --interval 1h --limit 24 --start-time 2026-01-01
```

Exit the environment:
```
exit
```