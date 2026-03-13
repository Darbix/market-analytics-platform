from sqlalchemy import Column, Integer, String, DateTime, Enum
from datetime import datetime
from app.core.base import Base
from app.models.enums import JobStatus


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    symbol = Column(String, index=True)
    interval = Column(String)
    job_type = Column(String, default="default")
    status = Column(
        Enum(JobStatus, name="job_status_enum"),
        default=JobStatus.PENDING,
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.utcnow)
