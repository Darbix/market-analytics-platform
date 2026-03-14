import pytest
from sqlalchemy import select

from app.models.job import Job
from app.models.analysis_result import AnalysisResult
from app.models.enums import JobStatus
from app.workers.tasks import run_analysis_logic, download_price_history_logic
from app.models.price_history import PriceHistory


@pytest.mark.asyncio
async def test_run_analysis_logic(db_session, mocker):
    # Mock Binance data and API
    mock_data = []
    for i in range(20):
        price = 100 + i
        # Fields: [OT, OP, HP, LP, CP, V, CT, _, _, _, _, _]
        mock_data.append([i*1000, price, price+1, price-1, price, 100, i*1000+999, 0, 0, 0, 0, 0])
        
    mocker.patch(
        "app.workers.tasks.fetch_klines",
        return_value=mock_data
    )

    job = Job(status=JobStatus.PENDING)

    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    await db_session.run_sync(
        lambda sync_session: run_analysis_logic(
            session=sync_session,
            job_id=job.id,
            symbol="BTCUSDT",
            interval="1d",
            limit=20,
            start_time=None,
            end_time=None,
            monte_carlo_runs=100
        )
    )

    await db_session.commit()
    await db_session.refresh(job)

    assert job.status == JobStatus.COMPLETED

    result = await db_session.execute(
        select(AnalysisResult).where(AnalysisResult.job_id == job.id)
    )

    analysis = result.scalar_one()

    assert analysis.job_id == job.id


@pytest.mark.asyncio
async def test_download_price_history_logic(db_session, mocker):

    mocker.patch(
        "app.workers.tasks.fetch_klines",
        return_value=[
            [1000,1,2,0.5,1.5,10,2000,0,0,0,0,0],
            [2000,1.5,2.5,1,2,12,3000,0,0,0,0,0],
        ]
    )

    job = Job(status=JobStatus.PENDING)

    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    assert job.status == JobStatus.PENDING

    await db_session.run_sync(
        lambda s: download_price_history_logic(
            s,
            job.id,
            "BTCUSDT",
            "1m",
            2,
            None,
            None
        )
    )

    await db_session.commit()
    await db_session.refresh(job)

    assert job.status == JobStatus.COMPLETED

    result = await db_session.execute(
        select(PriceHistory)
    )

    rows = result.scalars().all()

    assert len(rows) == 2
