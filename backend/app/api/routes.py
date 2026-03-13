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
from app.models.enums import JobStatus
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
# Generic job status retrieval
# -----------------------------
@router.get("/jobs/{job_id}")
async def get_job(job_id: int, session: AsyncSessionLocal = Depends(get_session)):
    result = await session.execute(
        select(Job).where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()

    if not job:
        return {"error": "Job not found"}

    return {
        "job_id": job.id,
        "status": job.status.value,
        "job_type": job.job_type
    }


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
        req.start_time,
        req.end_time,
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
        result = await session.execute(
            select(Job).where(Job.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            return {"error": "Job not found"}

        return {
            "job_id": job.id,
            "status": job.status.value,
            "data": None
        }

    return {
        "job_id": job_id,
        "status": JobStatus.COMPLETED,
        "data": {
            "volatility": analysis.volatility,
            "rsi_last": analysis.rsi_last,
            "monte_carlo_mean": analysis.monte_carlo_mean
        }
    }


# -----------------------------
# Price history endpoints
# -----------------------------
@router.post("/price-history")
async def download_price_history(req: PriceHistoryRequest, session: AsyncSessionLocal = Depends(get_session)):
    job = Job(
        symbol=req.symbol.upper(),
        interval=req.interval,
        status=JobStatus.PENDING,
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
        req.start_time,
        req.end_time
    )

    return {"job_id": job.id}


@router.get("/price-history/{symbol}")
async def get_prices(
    symbol: str,
    interval: str = "1m",
    limit: int = 100,
    start_time: datetime | None = Query(None),
    end_time: datetime | None = Query(None),
    session: AsyncSessionLocal = Depends(get_session)
):
    query = select(PriceHistory).where(
        PriceHistory.symbol == symbol.upper(),
        PriceHistory.interval == interval
    )

    if start_time:
        query = query.where(PriceHistory.timestamp >= start_time)
    if end_time:
        query = query.where(PriceHistory.timestamp <= end_time)

    if not start_time:
        query = query.order_by(PriceHistory.timestamp.desc()).limit(limit)
    else:
        query = query.order_by(PriceHistory.timestamp.asc()).limit(limit)

    result = await session.execute(query)
    rows = result.scalars().all()

    rows = sorted(rows, key=lambda x: x.timestamp)

    data = None
    if rows:
        data = {
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

    return {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_time,
        "endTime": end_time,
        "data": data
    }
