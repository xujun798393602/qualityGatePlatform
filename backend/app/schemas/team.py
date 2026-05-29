from typing import Optional
from pydantic import BaseModel


class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None
    leader_id: Optional[str] = None


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    leader_id: Optional[str] = None
    is_active: Optional[bool] = None


class TeamResponse(TeamBase):
    id: str
    is_active: bool

    class Config:
        from_attributes = True
