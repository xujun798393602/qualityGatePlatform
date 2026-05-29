import uuid
from sqlalchemy import Column, String, ForeignKey
from app.models.base import Base


class GateCondition(Base):
    __tablename__ = "gate_conditions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    gate_id = Column(String, ForeignKey("gates.id"), nullable=False)
    metric = Column(String(50), nullable=False)  # coverage, test_pass_rate, duplication, complexity, vulnerabilities
    operator = Column(String(10), nullable=False)  # >=, <=, ==, !=, >, <
    value = Column(String(50), nullable=False)
    unit = Column(String(20), nullable=True)  # %, count, etc.
