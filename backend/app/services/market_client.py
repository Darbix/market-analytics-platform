import requests
from datetime import datetime

from app.core.config import settings


def fetch_klines(
    symbol: str, interval: str, limit: int,
    start_time: datetime | None = None, end_time: datetime | None = None
):
    params={
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    }
    if start_time:
        params["startTime"] = int(start_time.timestamp() * 1000)
    if end_time:
        params["endTime"] = int(end_time.timestamp() * 1000)
    
    response = requests.get(
        settings.binance_url,
        params,
        timeout=10,
    )

    response.raise_for_status()
    return response.json()
