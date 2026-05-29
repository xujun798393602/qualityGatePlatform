from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.script import Script
from app.schemas.script import ScriptCreate, ScriptUpdate, ScriptResponse

router = APIRouter()


@router.get("/", response_model=List[ScriptResponse])
async def get_scripts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Script).where(Script.is_active == True))
    scripts = result.scalars().all()
    return scripts


@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script(
    script_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Script).where(Script.id == script_id))
    script = result.scalars().first()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    return script


@router.post("/", response_model=ScriptResponse)
async def create_script(
    script_data: ScriptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    script = Script(**script_data.model_dump(), created_by=current_user.id)
    db.add(script)
    await db.commit()
    await db.refresh(script)
    return script


@router.put("/{script_id}", response_model=ScriptResponse)
async def update_script(
    script_id: str,
    script_data: ScriptUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Script).where(Script.id == script_id))
    script = result.scalars().first()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    for field, value in script_data.model_dump(exclude_unset=True).items():
        setattr(script, field, value)
    await db.commit()
    await db.refresh(script)
    return script


@router.delete("/{script_id}")
async def delete_script(
    script_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Script).where(Script.id == script_id))
    script = result.scalars().first()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    script.is_active = False
    await db.commit()
    return {"message": "Script deleted"}


@router.post("/{script_id}/execute")
async def execute_script(
    script_id: str,
    params: dict = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Script).where(Script.id == script_id))
    script = result.scalars().first()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    # TODO: 实现真实脚本执行逻辑
    return {"result": {"status": "success", "output": f"Script '{script.name}' executed successfully"}}
