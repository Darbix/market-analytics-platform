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


## Project Structure

```bash
.
├── app/
│   ├── api/          # FastAPI routes and Pydantic schemas
│   ├── core/         # Configuration (env vars) and database setup
│   ├── models/       # SQLAlchemy ORM models
│   ├── services/     # Market data processing and business logic
│   └── workers/      # Celery background tasks and async processing
├── frontend/         # Frontend React web application
└── docker/           # Dockerfile configuration
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
cd frontend
npm install
npm run dev -- --host
```

