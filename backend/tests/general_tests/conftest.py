import os
import pytest
import pytest_asyncio
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.base import Base
from app.api.routes import get_session
from app.workers.celery_app import celery_app


# -----------------------
# Database configuration
# -----------------------
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# -----------------------
# Database fixtures
# -----------------------
@pytest_asyncio.fixture(scope="session")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest_asyncio.fixture
async def db_session(setup_db):
    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


# -----------------------
# API Client
# -----------------------
@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# -----------------------
# Service mocks
# -----------------------
@pytest.fixture(autouse=True)
def celery_control(request):
    """
    Default behavior:
        Celery tasks are mocked (not executed)

    To run task logic synchronously:
        @pytest.mark.celery(sync=True)
    """

    from app.workers.tasks import (
        task_run_analysis,
        task_download_price_history,
    )

    marker = request.node.get_closest_marker("celery")
    run_sync = marker and marker.kwargs.get("sync", False)

    if run_sync:
        # Run tasks immediately
        celery_app.conf.task_always_eager = True
        celery_app.conf.task_eager_propagates = True
        yield
        celery_app.conf.task_always_eager = False
    else:
        # Disable celery tasks globally
        with patch("celery.app.task.Task.apply_async", return_value=None):
            yield
