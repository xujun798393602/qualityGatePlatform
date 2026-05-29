from typing import Optional, List
from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: Optional[List[str]] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    id: str
    is_active: bool

    class Config:
        from_attributes = True
