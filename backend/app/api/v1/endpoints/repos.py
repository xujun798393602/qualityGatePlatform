from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/")
async def get_repos(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # TODO: 实现仓库查询
    return []


@router.get("/{repo_id}")
async def get_repo(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # TODO: 实现单个仓库查询
    return {}


@router.post("/")
async def create_repo(
    repo_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # TODO: 实现仓库创建
    return repo_data


@router.put("/{repo_id}")
async def update_repo(
    repo_id: str,
    repo_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # TODO: 实现仓库更新
    return repo_data


@router.delete("/{repo_id}")
async def delete_repo(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # TODO: 实现仓库删除
    return {"message": "Repo deleted"}


@router.post("/{repo_id}/sync")
async def sync_repo(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # TODO: 实现仓库同步
    return {"message": "Repo synced successfully"}


@router.get("/{repo_id}/branches")
async def get_repo_branches(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # TODO: 实现分支查询
    return ["main", "develop"]
