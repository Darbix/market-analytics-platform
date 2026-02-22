from app.core.database_async import engine
from app.core.base import Base
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # Automatically creates tables if they don’t exist
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Market Analytics Platform", lifespan=lifespan)

app.include_router(router)

# @app.get("/health")
# async def health():
#     return {"status": "ok"}

