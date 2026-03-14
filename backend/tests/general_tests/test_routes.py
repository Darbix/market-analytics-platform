import pytest
from fastapi import status
from datetime import datetime, timezone

from app.models.job import Job
from app.models.enums import JobStatus
from app.models.price_history import PriceHistory


@pytest.mark.asyncio
async def test_health(client):
    res = await client.get("/health")

    assert res.status_code == status.HTTP_200_OK
    assert res.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_get_job_status(db_session, client):
    job = Job(status=JobStatus.PENDING)

    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    res = await client.get(f"/jobs/{job.id}")

    assert res.status_code == status.HTTP_200_OK

    data = res.json()

    assert data["job_id"] == job.id
    assert data["status"] == JobStatus.PENDING

@pytest.mark.asyncio
async def test_get_job_twice(db_session, client):
    job1 = Job()
    job2 = Job()

    db_session.add(job1)
    db_session.add(job2)

    await db_session.commit()
    await db_session.refresh(job1)
    await db_session.refresh(job2)

    for job in [job1, job2]:
        res = await client.get(f"/jobs/{job.id}")

        assert res.status_code == status.HTTP_200_OK

        data = res.json()

        assert data["job_id"] == job.id
        assert data["status"] == JobStatus.PENDING


@pytest.mark.asyncio
async def test_job_not_found(client):
    res = await client.get("/jobs/999")

    assert res.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_create_analysis_job(client):

    res = await client.post("/analysis", json={
        "symbol": "BTCUSDT",
        "interval": "1m",
        "limit": 20
    })

    assert res.status_code == status.HTTP_200_OK

    data = res.json()

    assert "job_id" in data


@pytest.mark.asyncio
async def test_analysis_pending(client):

    res = await client.post("/analysis", json={
        "symbol": "BTCUSDT",
        "interval": "1m",
        "limit": 20
    })

    job_id = res.json()["job_id"]

    res = await client.get(f"/analysis/{job_id}")

    assert res.status_code == status.HTTP_200_OK

    data = res.json()

    assert data["job_id"] == 1
    assert data["status"] == JobStatus.PENDING
    assert data["data"] is None


@pytest.mark.asyncio
async def test_analysis_not_found(client):
    res = await client.get("/analysis/999")

    assert res.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_create_job_price_history(client):

    res = await client.post("/price-history", json={
        "symbol": "BTCUSDT",
        "interval": "1m",
        "limit": 10
    })

    assert res.status_code == status.HTTP_200_OK

    data = res.json()

    assert data["job_id"] == 1


@pytest.mark.asyncio
async def test_get_price_history_empty(client):

    res = await client.get("/price-history/BTCUSDT")

    assert res.status_code == status.HTTP_200_OK

    data = res.json()

    assert data["symbol"] == "BTCUSDT"
    assert data["data"] is None


@pytest.mark.asyncio
async def test_get_price_history_with_data(client, db_session):
    params = {
        "timestamp": datetime(2026, 1, 31, 12, 30, 0, tzinfo=timezone.utc),
        "open": 50000,
        "high": 80000,
        "low": 10000,
        "close": 55000,
        "volume": 10
    }

    price = PriceHistory(
        symbol="BTCUSDT",
        interval="1m",
        timestamp=params["timestamp"],
        open=params["open"],
        high=params["high"],
        low=params["low"],
        close=params["close"],
        volume=params["volume"]
    )

    db_session.add(price)
    await db_session.commit()

    res = await client.get("/price-history/BTCUSDT")

    assert res.status_code == status.HTTP_200_OK

    data = res.json()
    prices = data["data"]["prices"]

    assert data["symbol"] == "BTCUSDT"
    assert data["interval"] == "1m"
    assert data["startTime"] == None
    assert data["endTime"] == None

    iso_timestamp = params.pop("timestamp").isoformat()
    params["timestamp"] = iso_timestamp

    data_candle = data["data"]["prices"][0]
    
    for key, value in params.items():
        assert data_candle[key] == value
