import uuid
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func
from app.models.base import Base


class PipelineRunStage(Base):
    __tablename__ = "pipeline_run_stages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, nullable=False)
    stage_name = Column(String(100), nullable=False)
    status = Column(String(20), default="pending")  # pending, running, success, failed, skipped
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    output = Column(Text, nullable=True)
