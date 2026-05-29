import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey
from app.models.base import Base


class GateCheckResult(Base):
    __tablename__ = "gate_check_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    check_id = Column(String, ForeignKey("gate_checks.id"), nullable=False)
    metric = Column(String(50), nullable=False)
    expected = Column(String(50), nullable=False)
    actual = Column(String(50), nullable=False)
    passed = Column(Boolean, default=False)
