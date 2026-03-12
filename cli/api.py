import requests
from cli.config import settings
from datetime import datetime


def _format_payload(payload: dict):
    """Helper to clean None values and format datetimes for JSON."""
    return {
        k: (v.isoformat() if isinstance(v, datetime) else v)
        for k, v in payload.items()
        if v is not None
    }


def request_price_history(symbol: str, interval: str, limit: int,
    start_time: datetime | None, end_time: datetime | None
):
    data = _format_payload({
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
        "startTime": start_time,
        "endTime": end_time
    })
    res = requests.post(f"{settings.market_api_url}/price-history", json=data)
    res.raise_for_status()
    return res.json()


def run_analysis(symbol: str, interval: str, limit: int,
    start_time: datetime | None, end_time: datetime | None, monte_carlo_runs: int
):
    data = _format_payload({
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
        "startTime": start_time,
        "endTime": end_time,
        "monte_carlo_runs": monte_carlo_runs
    })
    res = requests.post(f"{settings.market_api_url}/analysis", json=data)
    res.raise_for_status()
    return res.json()


def get_job(job_id: int):
    res = requests.get(f"{settings.market_api_url}/jobs/{job_id}")
    res.raise_for_status()
    return res.json()


def get_analysis(job_id: int):
    res = requests.get(f"{settings.market_api_url}/analysis/{job_id}")
    res.raise_for_status()
    return res.json()


def get_prices(symbol: str, interval: str, limit: int,
    start_time: datetime | None, end_time: datetime | None
):
    url = f"{settings.market_api_url}/price-history/{symbol}"
    params = _format_payload({
        "interval": interval,
        "limit": limit,
        "startTime": start_time,
        "endTime": end_time
    })
    res = requests.get(f"{settings.market_api_url}/price-history/{symbol}", params=params)
    res.raise_for_status()
    return res.json()["data"]
