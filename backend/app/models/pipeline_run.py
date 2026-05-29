import uuid
from sqlalchemy import Column, String, DateTime, Integer, Float
from sqlalchemy.sql import func
from app.models.base import Base


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pipeline_id = Column(String, nullable=False)
    status = Column(String(20), default="pending")  # pending, running, success, failed
    trigger_type = Column(String(20), default="manual")
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Float, nullable=True)  # seconds
    created_by = Column(String, nullable=True)
