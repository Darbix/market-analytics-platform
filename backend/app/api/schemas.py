from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class TrackRequest(BaseModel):
    symbol: str
    interval: str = "1m"

class AnalysisRequest(BaseModel):
    symbol: str
    interval: str = "1m"
    limit: int = 10
    # Optional time (ISO 8601) parameters
    start_time: datetime | None = Field(None, alias="startTime")
    end_time: datetime | None = Field(None, alias="endTime")
    monte_carlo_runs: int = 1000

    model_config = ConfigDict(populate_by_name=True)

class PriceHistoryRequest(BaseModel):
    symbol: str
    interval: str = "1m"
    limit: int = 10
    # Optional time (ISO 8601) parameters
    start_time: datetime | None = Field(None, alias="startTime")
    end_time: datetime | None = Field(None, alias="endTime")

    model_config = ConfigDict(populate_by_name=True)
