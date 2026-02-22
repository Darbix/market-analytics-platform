import requests
from datetime import datetime

from app.core.config import settings


def fetch_klines(
    symbol: str, interval: str, limit: int,
    startTime: datetime | None = None, endTime: datetime | None = None
):
    params={
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    }
    if startTime:
        params["startTime"] = int(startTime.timestamp() * 1000)
    if endTime:
        params["endTime"] = int(endTime.timestamp() * 1000)
    
    response = requests.get(
        settings.binance_url,
        params,
        timeout=10,
    )

    response.raise_for_status()
    return response.json()
