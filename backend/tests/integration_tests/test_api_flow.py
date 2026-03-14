# import os
# import httpx
# import time
# from fastapi import status

# from app.models.enums import JobStatus


# TEST_API_URL = os.getenv('TEST_API_URL', 'http://localhost:8000')


# def test_health_endpoint():
#     res = httpx.get(f"{TEST_API_URL}/health")

#     assert res.status_code == status.HTTP_200_OK
#     assert res.json() == {"status": "ok"}


# def test_full_analysis_flow():
#     res = httpx.post(
#         f"{TEST_API_URL}/analysis",
#         json={
#             "symbol": "BTCUSDT",
#             "interval": "1m",
#             "limit": 20
#         }
#     )

#     assert res.status_code == status.HTTP_200_OK

#     job_id = res.json()["job_id"]

#     # wait until worker finishes
#     for _ in range(30):
#         res = httpx.get(f"{TEST_API_URL}/analysis/{job_id}")

#         data = res.json()
#         print(data)

#         if data["status"] == JobStatus.COMPLETED:
#             assert data["data"] is not None
#             assert "volatility" in data["data"]
#             return

#         time.sleep(1)

#     raise AssertionError("Analysis job did not complete")



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
