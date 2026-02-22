from typing import List
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.core.database_async import AsyncSessionLocal
from app.core.config import settings
from app.models.job import Job
from app.models.analysis_result import AnalysisResult
from app.models.price_history import PriceHistory
from app.workers.tasks import task_run_analysis, task_download_price_history
from app.api.schemas import TrackRequest, AnalysisRequest, PriceHistoryRequest

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

router = APIRouter()


# -----------------------------
# Dependency for database session
# -----------------------------
async def get_session() -> AsyncSessionLocal:
    async with AsyncSessionLocal() as session:
        yield session


# -----------------------------
# Health check
# -----------------------------
@router.get("/health")
async def health():
    return {"status": "ok"}


# -----------------------------
# Track a market symbol
# -----------------------------
@router.post("/track")
async def track_market(req: TrackRequest, session: AsyncSessionLocal = Depends(get_session)):
    job = Job(symbol=req.symbol, interval=req.interval)
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return {"job_id": job.id}


# -----------------------------
# Analysis endpoints
# -----------------------------
@router.post("/analysis")
async def create_analysis(req: AnalysisRequest, session: AsyncSessionLocal = Depends(get_session)):
    job = Job(symbol=req.symbol, interval=req.interval)
    session.add(job)
    await session.commit()
    await session.refresh(job)

    task_run_analysis.delay(
        job.id,
        req.symbol,
        req.interval,
        req.limit,
        req.startTime,
        req.endTime,
        req.monte_carlo_runs
    )

    return {"job_id": job.id}


@router.get("/analysis/{job_id}")
async def get_analysis(job_id: int, session: AsyncSessionLocal = Depends(get_session)):
    result = await session.execute(
        select(AnalysisResult).where(AnalysisResult.job_id == job_id)
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        return {"status": "processing"}

    return {
        "volatility": analysis.volatility,
        "rsi_last": analysis.rsi_last,
        "monte_carlo_mean": analysis.monte_carlo_mean,
    }


# -----------------------------
# Price history endpoints
# -----------------------------
# TODO time range of the history-plot I want to see
@router.post("/price_history")
async def download_price_history(req: PriceHistoryRequest, session: AsyncSessionLocal = Depends(get_session)):
    job = Job(
        symbol=req.symbol.upper(),
        interval=req.interval,
        status="pending",
        job_type="price_history"
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    task_download_price_history.delay(
        job.id,
        req.symbol.upper(),
        req.interval,
        req.limit,
        req.startTime,
        req.endTime,
    )

    return {"job_id": job.id}


@router.get("/price_history/{symbol}")
async def get_prices(
    symbol: str,
    interval: str = "1m",
    limit: int = 100,
    startTime: datetime | None = Query(None),
    endTime: datetime | None = Query(None),
    session: AsyncSessionLocal = Depends(get_session)
):
    # result = await session.execute(
    #     select(PriceHistory)
    #     .where(PriceHistory.symbol == symbol.upper())
    #     .where(PriceHistory.interval == interval)
    #     .order_by(PriceHistory.timestamp.desc())
    #     .limit(limit)
    # )
    query = select(PriceHistory).where(
        PriceHistory.symbol == symbol.upper(),
        PriceHistory.interval == interval
    )

    if startTime:
        query = query.where(PriceHistory.timestamp >= startTime)
    if endTime:
        query = query.where(PriceHistory.timestamp <= endTime)

    query = query.order_by(PriceHistory.timestamp.desc()).limit(limit)

    result = await session.execute(query)

    rows = result.scalars().all()

    # sort ascending for chart display
    rows = sorted(rows, key=lambda x: x.timestamp)

    return {
        "symbol": symbol,
        "interval": interval,
        "prices": [
            {
                "timestamp": x.timestamp.isoformat(),
                "open": x.open,
                "high": x.high,
                "low": x.low,
                "close": x.close,
                "volume": x.volume
            }
            for x in rows
        ]
    }
