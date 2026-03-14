import time
from fastapi import status


def wait_for_analysis_job(client, job_id, timeout=120):
    """Poll job status until completed."""
    start = time.time()
    delay = 2
    status = "UNKNOWN"

    while time.time() - start < timeout:
        res = client.get(f"/analysis/{job_id}")
        res.raise_for_status()

        data = res.json()
        status = data["status"]

        if status == "COMPLETED":
            return data
        elif status == "FAILED":
            break

        time.sleep(delay)

    raise TimeoutError(f"Job {job_id} did not complete in {timeout} s. Status: {status}.")


def test_health_endpoint(client):
    r = client.get("/health")

    assert r.status_code == status.HTTP_200_OK
    assert r.json() == {"status": "ok"}


def test_full_analysis_flow(client):
    r = client.post(
        "/analysis",
        json={
            "symbol": "BTCUSDT",
            "interval": "1d",
            "limit": 20,
        },
    )

    assert r.status_code == status.HTTP_200_OK

    job_id = r.json()["job_id"]

    result = wait_for_analysis_job(client, job_id)

    assert result["data"] is not None
    assert "volatility" in result["data"]
