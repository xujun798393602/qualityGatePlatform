from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.repo import Repo
from app.schemas.repo import RepoCreate, RepoUpdate, RepoResponse

router = APIRouter()


@router.get("/", response_model=List[RepoResponse])
async def get_repos(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Repo).where(Repo.is_active == True))
    repos = result.scalars().all()
    return repos


@router.get("/{repo_id}", response_model=RepoResponse)
async def get_repo(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Repo).where(Repo.id == repo_id))
    repo = result.scalars().first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
    return repo


@router.post("/", response_model=RepoResponse)
async def create_repo(
    repo_data: RepoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    repo = Repo(**repo_data.model_dump(), created_by=current_user.id)
    db.add(repo)
    await db.commit()
    await db.refresh(repo)
    return repo


@router.put("/{repo_id}", response_model=RepoResponse)
async def update_repo(
    repo_id: str,
    repo_data: RepoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Repo).where(Repo.id == repo_id))
    repo = result.scalars().first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
    for field, value in repo_data.model_dump(exclude_unset=True).items():
        setattr(repo, field, value)
    await db.commit()
    await db.refresh(repo)
    return repo


@router.delete("/{repo_id}")
async def delete_repo(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Repo).where(Repo.id == repo_id))
    repo = result.scalars().first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
    repo.is_active = False
    await db.commit()
    return {"message": "Repo deleted"}


@router.post("/{repo_id}/sync")
async def sync_repo(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Repo).where(Repo.id == repo_id))
    repo = result.scalars().first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
    # TODO: 实现 GitLab 同步逻辑
    repo.last_sync_at = datetime.utcnow()
    await db.commit()
    return {"message": "Repo synced successfully"}


@router.get("/{repo_id}/branches")
async def get_repo_branches(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Repo).where(Repo.id == repo_id))
    repo = result.scalars().first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
    # TODO: 从 GitLab 获取真实分支列表
    return ["main", "develop", "feature/*"]
