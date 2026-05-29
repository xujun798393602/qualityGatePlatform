from typing import Optional
from pydantic import BaseModel


class RepoBase(BaseModel):
    name: str
    url: str
    description: Optional[str] = None
    branch: str = "main"
    type: str = "gitlab"


class RepoCreate(RepoBase):
    gitlab_project_id: Optional[int] = None
    access_token: Optional[str] = None


class RepoUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    branch: Optional[str] = None
    type: Optional[str] = None
    gitlab_project_id: Optional[int] = None
    access_token: Optional[str] = None
    is_active: Optional[bool] = None


class RepoResponse(RepoBase):
    id: str
    gitlab_project_id: Optional[int] = None
    is_active: bool
    last_sync_at: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
