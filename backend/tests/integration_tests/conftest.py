import os
import time
import httpx
import pytest


TEST_API_URL = os.getenv("TEST_API_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def client():
    """Reusable HTTP client for integration tests."""
    with httpx.Client(base_url=TEST_API_URL, timeout=10) as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def wait_for_api(client):
    """Wait until API container is ready."""
    timeout = 90
    start = time.time()
    delay = 2

    print(f"\n[conftest] Waiting for API at {TEST_API_URL}...")

    while time.time() - start < timeout:
        try:
            res = client.get("/health")
            if res.status_code == httpx.codes.OK:
                elapsed = round(time.time() - start, 2)
                print(f"[conftest] API ready after {elapsed} s.")
                return
        except httpx.HTTPError:
            pass

        time.sleep(delay)

    raise RuntimeError(f"API did not start in {timeout} s.")
