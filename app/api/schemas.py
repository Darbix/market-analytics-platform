from pydantic import BaseModel
from datetime import datetime

class TrackRequest(BaseModel):
    symbol: str
    interval: str = "1m"

class AnalysisRequest(BaseModel):
    symbol: str
    interval: str = "1m"
    limit: int = 10
    # Optional time (ISO 8601) parameters
    startTime: datetime | None = None   # The oldest time
    endTime: datetime | None = None     # The latest time
    
    monte_carlo_runs: int = 1000

class PriceHistoryRequest(BaseModel):
    symbol: str
    interval: str = "1m"
    limit: int = 10
    # Optional time (ISO 8601) parameters
    startTime: datetime | None = None   # The oldest time
    endTime: datetime | None = None     # The latest time
