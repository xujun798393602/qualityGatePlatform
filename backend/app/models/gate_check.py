import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.models.base import Base


class GateCheck(Base):
    __tablename__ = "gate_checks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    gate_id = Column(String, nullable=False)
    run_id = Column(String, nullable=True)
    passed = Column(Boolean, default=False)
    checked_at = Column(DateTime(timezone=True), server_default=func.now())
