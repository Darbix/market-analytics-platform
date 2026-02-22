from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from app.core.base import Base
from datetime import datetime


class PriceHistory(Base):
    # A table for price data candles
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True)
    symbol = Column(String, index=True)
    interval = Column(String)
    timestamp = Column(DateTime)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)

    # Prevent duplicates of the unique combination of attributes
    __table_args__ = (
        UniqueConstraint("symbol", "interval", "timestamp", name="uq_price"),
    )
