from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


engine_sync = create_engine(settings.database_url.replace("+asyncpg", ""), echo=True)

SessionLocal = sessionmaker(
    bind=engine_sync,
    autoflush=False,
    autocommit=False,
)
