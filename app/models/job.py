from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.core.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    symbol = Column(String, index=True)
    interval = Column(String)
    job_type = Column(String, default="default")
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
