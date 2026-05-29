from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/")
async def get_scripts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # TODO: 实现脚本查询
    return []


@router.get("/{script_id}")
async def get_script(
    script_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # TODO: 实现单个脚本查询
    return {}


@router.post("/")
async def create_script(
    script_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # TODO: 实现脚本创建
    return script_data


@router.put("/{script_id}")
async def update_script(
    script_id: str,
    script_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # TODO: 实现脚本更新
    return script_data


@router.delete("/{script_id}")
async def delete_script(
    script_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # TODO: 实现脚本删除
    return {"message": "Script deleted"}


@router.post("/{script_id}/execute")
async def execute_script(
    script_id: str,
    params: dict = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # TODO: 实现脚本执行
    return {"result": {"status": "success", "output": "Script executed successfully"}}
