import uuid
from sqlalchemy import Column, String, Integer, ForeignKey
from app.models.base import Base


class PipelineStage(Base):
    __tablename__ = "pipeline_stages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pipeline_id = Column(String, ForeignKey("pipelines.id"), nullable=False)
    name = Column(String(100), nullable=False)
    order = Column(Integer, default=0)
    script_id = Column(String, ForeignKey("scripts.id"), nullable=True)
    status = Column(String(20), default="pending")  # pending, running, success, failed, skipped
