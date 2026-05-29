from typing import Optional, List
from pydantic import BaseModel


class PipelineStageBase(BaseModel):
    name: str
    order: int = 0
    script_id: Optional[str] = None


class PipelineStageCreate(PipelineStageBase):
    pass


class PipelineStageResponse(PipelineStageBase):
    id: str
    status: str = "pending"

    class Config:
        from_attributes = True


class PipelineBase(BaseModel):
    name: str
    description: Optional[str] = None
    repo_id: Optional[str] = None
    branch: str = "main"
    trigger_type: str = "manual"


class PipelineCreate(PipelineBase):
    stages: Optional[List[PipelineStageCreate]] = None


class PipelineUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    repo_id: Optional[str] = None
    branch: Optional[str] = None
    trigger_type: Optional[str] = None
    is_active: Optional[bool] = None
    stages: Optional[List[PipelineStageCreate]] = None


class PipelineResponse(PipelineBase):
    id: str
    status: str = "idle"
    is_active: bool
    last_run_at: Optional[str] = None
    last_run_status: Optional[str] = None
    stages: Optional[List[PipelineStageResponse]] = None
    created_by: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class PipelineRunStageResponse(BaseModel):
    id: str
    stage_name: str
    status: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    output: Optional[str] = None

    class Config:
        from_attributes = True


class PipelineRunResponse(BaseModel):
    id: str
    pipeline_id: str
    status: str
    trigger_type: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    duration: Optional[float] = None
    stages: Optional[List[PipelineRunStageResponse]] = None
    created_by: Optional[str] = None

    class Config:
        from_attributes = True
