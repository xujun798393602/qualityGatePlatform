from typing import Optional, List
from pydantic import BaseModel


class GateConditionBase(BaseModel):
    metric: str
    operator: str
    value: str
    unit: Optional[str] = None


class GateConditionCreate(GateConditionBase):
    pass


class GateConditionResponse(GateConditionBase):
    id: str

    class Config:
        from_attributes = True


class GateBase(BaseModel):
    name: str
    description: Optional[str] = None
    pipeline_id: Optional[str] = None
    type: str = "quality"


class GateCreate(GateBase):
    conditions: Optional[List[GateConditionCreate]] = None


class GateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    pipeline_id: Optional[str] = None
    type: Optional[str] = None
    is_active: Optional[bool] = None
    conditions: Optional[List[GateConditionCreate]] = None


class GateResponse(GateBase):
    id: str
    is_active: bool
    conditions: Optional[List[GateConditionResponse]] = None
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class GateCheckResultResponse(BaseModel):
    metric: str
    expected: str
    actual: str
    passed: bool

    class Config:
        from_attributes = True


class GateCheckResponse(BaseModel):
    id: str
    gate_id: str
    gate_name: Optional[str] = None
    passed: bool
    checked_at: Optional[str] = None
    conditions: Optional[List[GateCheckResultResponse]] = None

    class Config:
        from_attributes = True
