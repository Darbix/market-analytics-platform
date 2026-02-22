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
from app.services.market_client import fetch_klines
from app.services.price_data_service import parse_klines
from app.services.analysis_service import compute_analysis

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@celery_app.task
def task_run_analysis(job_id: int, symbol: str, interval: str, limit: int,
    startTime: datetime | None, endTime: datetime | None, monte_carlo_runs: int
):
    session = SessionLocal()

    try:
        data = fetch_klines(symbol, interval, limit, startTime, endTime)

        result_data = compute_analysis(data, monte_carlo_runs)

        result = AnalysisResult(
            job_id=job_id,
            **result_data
        )

        session.add(result)

        session.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(status="completed")
        )

        session.commit()

    except Exception as e:
        session.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(status="failed")
        )
        session.commit()
        logger.error(f"The analysis process for the job {job_id} failed: {e}")

    finally:
        session.close()


@celery_app.task
def task_download_price_history(
    job_id: int, symbol: str, interval: str, limit: int,
    startTime: datetime | None, endTime: datetime | None
):
    session = SessionLocal()

    try:
        data = fetch_klines(symbol, interval, limit, startTime, endTime)

        rows = parse_klines(symbol, interval, data)

        # Bulk insert
        stmt = insert(PriceHistory).values(rows)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=["symbol", "interval", "timestamp"]
        )
        session.execute(stmt)

        session.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(status="completed")
        )

        session.commit()

    except Exception as e:
        session.execute(
            update(Job)
            .where(Job.id == job_id)
            .values(status="failed")
        )
        session.commit()
        logger.error(f"Price history job {job_id} failed: {e}")

    finally:
        session.close()
