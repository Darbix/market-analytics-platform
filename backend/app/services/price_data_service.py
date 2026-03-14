from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import insert
from app.models.price_history import PriceHistory


def parse_klines(symbol: str, interval: str, data: list):
    rows = []

    for kline in data:
        open_time, open_, high, low, close, volume, *_ = kline

        rows.append({
            "symbol": symbol,
            "interval": interval,
            "timestamp": datetime.fromtimestamp(open_time / 1000, tz=timezone.utc),
            "open": float(open_),
            "high": float(high),
            "low": float(low),
            "close": float(close),
            "volume": float(volume),
        })

    return rows
