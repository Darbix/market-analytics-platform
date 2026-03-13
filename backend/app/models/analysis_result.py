from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), unique=True)

    volatility = Column(Float)
    rsi_last = Column(Float)
    monte_carlo_mean = Column(Float)

    job = relationship("Job")
