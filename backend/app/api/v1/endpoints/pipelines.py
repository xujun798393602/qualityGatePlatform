from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.pipeline import Pipeline
from app.models.pipeline_stage import PipelineStage
from app.models.pipeline_run import PipelineRun
from app.models.pipeline_run_stage import PipelineRunStage
from app.schemas.pipeline import PipelineCreate, PipelineUpdate, PipelineResponse, PipelineRunResponse

router = APIRouter()


@router.get("/", response_model=List[PipelineResponse])
async def get_pipelines(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Pipeline).where(Pipeline.is_active == True))
    pipelines = result.scalars().all()
    # Get stages for each pipeline
    for pipeline in pipelines:
        stages_result = await db.execute(
            select(PipelineStage).where(PipelineStage.pipeline_id == pipeline.id).order_by(PipelineStage.order)
        )
        pipeline.stages = stages_result.scalars().all()
    return pipelines


@router.get("/{pipeline_id}", response_model=PipelineResponse)
async def get_pipeline(
    pipeline_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Pipeline).where(Pipeline.id == pipeline_id))
    pipeline = result.scalars().first()
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    stages_result = await db.execute(
        select(PipelineStage).where(PipelineStage.pipeline_id == pipeline.id).order_by(PipelineStage.order)
    )
    pipeline.stages = stages_result.scalars().all()
    return pipeline


@router.post("/", response_model=PipelineResponse)
async def create_pipeline(
    pipeline_data: PipelineCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    stages_data = pipeline_data.stages or []
    pipeline_dict = pipeline_data.model_dump(exclude={"stages"})
    pipeline = Pipeline(**pipeline_dict, created_by=current_user.id)
    db.add(pipeline)
    await db.flush()
    # Create stages
    for stage_data in stages_data:
        stage = PipelineStage(**stage_data.model_dump(), pipeline_id=pipeline.id)
        db.add(stage)
    await db.commit()
    await db.refresh(pipeline)
    stages_result = await db.execute(
        select(PipelineStage).where(PipelineStage.pipeline_id == pipeline.id).order_by(PipelineStage.order)
    )
    pipeline.stages = stages_result.scalars().all()
    return pipeline


@router.put("/{pipeline_id}", response_model=PipelineResponse)
async def update_pipeline(
    pipeline_id: str,
    pipeline_data: PipelineUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Pipeline).where(Pipeline.id == pipeline_id))
    pipeline = result.scalars().first()
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    stages_data = pipeline_data.stages
    update_dict = pipeline_data.model_dump(exclude_unset=True, exclude={"stages"})
    for field, value in update_dict.items():
        setattr(pipeline, field, value)
    # Update stages if provided
    if stages_data is not None:
        # Delete old stages
        old_stages = await db.execute(
            select(PipelineStage).where(PipelineStage.pipeline_id == pipeline.id)
        )
        for stage in old_stages.scalars().all():
            await db.delete(stage)
        # Create new stages
        for stage_data in stages_data:
            stage = PipelineStage(**stage_data.model_dump(), pipeline_id=pipeline.id)
            db.add(stage)
    await db.commit()
    await db.refresh(pipeline)
    stages_result = await db.execute(
        select(PipelineStage).where(PipelineStage.pipeline_id == pipeline.id).order_by(PipelineStage.order)
    )
    pipeline.stages = stages_result.scalars().all()
    return pipeline


@router.delete("/{pipeline_id}")
async def delete_pipeline(
    pipeline_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Pipeline).where(Pipeline.id == pipeline_id))
    pipeline = result.scalars().first()
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    pipeline.is_active = False
    await db.commit()
    return {"message": "Pipeline deleted"}


@router.post("/{pipeline_id}/run", response_model=PipelineRunResponse)
async def run_pipeline(
    pipeline_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Pipeline).where(Pipeline.id == pipeline_id))
    pipeline = result.scalars().first()
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    # Create run record
    run = PipelineRun(
        pipeline_id=pipeline_id,
        status="running",
        trigger_type="manual",
        created_by=current_user.id,
    )
    db.add(run)
    await db.flush()
    # Get stages
    stages_result = await db.execute(
        select(PipelineStage).where(PipelineStage.pipeline_id == pipeline_id).order_by(PipelineStage.order)
    )
    stages = stages_result.scalars().all()
    # Create run stage records
    for stage in stages:
        run_stage = PipelineRunStage(
            run_id=run.id,
            stage_name=stage.name,
            status="pending",
        )
        db.add(run_stage)
    # Update pipeline status
    pipeline.status = "running"
    pipeline.last_run_at = datetime.utcnow()
    pipeline.last_run_status = "running"
    await db.commit()
    await db.refresh(run)
    # TODO: 实际执行流水线逻辑
    return run


@router.get("/{pipeline_id}/runs", response_model=List[PipelineRunResponse])
async def get_pipeline_runs(
    pipeline_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(PipelineRun).where(PipelineRun.pipeline_id == pipeline_id).order_by(PipelineRun.started_at.desc())
    )
    runs = result.scalars().all()
    return runs


@router.get("/{pipeline_id}/runs/{run_id}", response_model=PipelineRunResponse)
async def get_pipeline_run(
    pipeline_id: str,
    run_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(PipelineRun).where(PipelineRun.id == run_id, PipelineRun.pipeline_id == pipeline_id)
    )
    run = result.scalars().first()
    if not run:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    stages_result = await db.execute(
        select(PipelineRunStage).where(PipelineRunStage.run_id == run.id)
    )
    run.stages = stages_result.scalars().all()
    return run
