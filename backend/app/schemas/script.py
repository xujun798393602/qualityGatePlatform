from typing import Optional
from pydantic import BaseModel


class ScriptBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: str
    content: str
    language: str


class ScriptCreate(ScriptBase):
    pass


class ScriptUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    content: Optional[str] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None


class ScriptResponse(ScriptBase):
    id: str
    is_active: bool
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
