import numpy as np
import pandas as pd
import requests
import logging
from datetime import datetime

from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert

from app.workers.celery_app import celery_app
from app.core.database_sync import SessionLocal
from app.core.config import settings
from app.models.job import Job
from app.models.analysis_result import AnalysisResult
from app.models.price_history import PriceHistory
from app.models.enums import JobStatus
from app.services.market_client import fetch_klines
from app.services.price_data_service import parse_klines
from app.services.analysis_service import compute_analysis

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@celery_app.task
def task_run_analysis(
    job_id: int, symbol: str, interval: str, limit: int,
    start_time: datetime | None, end_time: datetime | None, monte_carlo_runs: int
):
    session = SessionLocal()

    try:
        run_analysis_logic(
            session,
            job_id,
            symbol,
            interval,
            limit,
            start_time,
            end_time,
            monte_carlo_runs
        )

        session.commit()

    except Exception as e:
        session.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(status=JobStatus.FAILED)
        )
        session.commit()
        logger.error(f"The analysis process for the job {job_id} failed: {e}")

    finally:
        session.close()


def run_analysis_logic(
    session, job_id: int, symbol: str, interval: str, limit: int,
    start_time: datetime | None, end_time: datetime | None, monte_carlo_runs: int
):
    session.execute(
        update(Job)
        .where(Job.id == job_id)
        .values(status=JobStatus.PROCESSING)
    )
    
    try:
        data = fetch_klines(symbol, interval, limit, start_time, end_time)
    except requests.HTTPError as e:
        # Catch HTTP errors, including 451
        session.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(status=JobStatus.UNAVAILABLE)
        )
        session.commit()
        logger.error(f"Job {job_id} failed with client HTTP error: {e}.")
        
        session.add(
            AnalysisResult(
                job_id=job_id,
                volatility=0,
                rsi_last=0,
                monte_carlo_mean=0
            )
        )
        return

    result_data = compute_analysis(data, monte_carlo_runs)

    result = AnalysisResult(
        job_id=job_id,
        **result_data
    )

    session.add(result)

    session.execute(
        update(Job)
        .where(Job.id == job_id)
        .values(status=JobStatus.COMPLETED)
    )


@celery_app.task
def task_download_price_history(
    job_id: int, symbol: str, interval: str, limit: int,
    start_time: datetime | None, end_time: datetime | None
):
    session = SessionLocal()

    try:
        download_price_history_logic(
            session,
            job_id,
            symbol,
            interval,
            limit,
            start_time,
            end_time
        )

        session.commit()

    except Exception as e:
        session.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(status=JobStatus.FAILED)
        )
        session.commit()
        logger.error(f"Price history job {job_id} failed: {e}")

    finally:
        session.close()


def download_price_history_logic(
    session, job_id: int, symbol: str, interval: str, limit: int,
    start_time: datetime | None, end_time: datetime | None
):
    # ---- Update job status ----
    session.execute(
        update(Job)
        .where(Job.id == job_id)
        .values(status=JobStatus.PROCESSING)
    )

    data = fetch_klines(symbol, interval, limit, start_time, end_time)

    if data:
        rows = parse_klines(symbol, interval, data)

        stmt = insert(PriceHistory).values(rows)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=["symbol", "interval", "timestamp"]
        )

        session.execute(stmt)

    session.execute(
        update(Job)
        .where(Job.id == job_id)
        .values(status=JobStatus.COMPLETED)
    )
