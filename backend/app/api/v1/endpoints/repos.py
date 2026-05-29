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
from app.services.gitlab_service import get_gitlab_service

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
    # 验证 GitLab 连接
    if repo_data.type == "gitlab" and repo_data.access_token:
        try:
            gitlab = get_gitlab_service(repo_data.url, repo_data.access_token)
            # 测试连接：获取项目信息
            if repo_data.gitlab_project_id:
                project = await gitlab.get_project(repo_data.gitlab_project_id)
                repo_data.name = repo_data.name or project.get("name", repo_data.name)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"GitLab 连接失败: {str(e)}")

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

    # 如果更新了 token，验证连接
    if repo_data.access_token and repo_data.type == "gitlab":
        try:
            url = repo_data.url or repo.url
            gitlab = get_gitlab_service(url, repo_data.access_token)
            project_id = repo_data.gitlab_project_id or repo.gitlab_project_id
            if project_id:
                await gitlab.get_project(project_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"GitLab 连接失败: {str(e)}")

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

    if not repo.access_token:
        raise HTTPException(status_code=400, detail="请先配置仓库访问令牌")

    try:
        gitlab = get_gitlab_service(repo.url, repo.access_token)
        if repo.gitlab_project_id:
            # 获取项目最新信息
            project = await gitlab.get_project(repo.gitlab_project_id)
            repo.name = project.get("name", repo.name)
            repo.description = project.get("description", repo.description)
            repo.last_sync_at = datetime.utcnow()
            await db.commit()
            return {"message": "同步成功", "project": project.get("name")}
        else:
            raise HTTPException(status_code=400, detail="请先配置 GitLab 项目 ID")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")


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

    if not repo.access_token or not repo.gitlab_project_id:
        return ["main", "develop"]

    try:
        gitlab = get_gitlab_service(repo.url, repo.access_token)
        branches = await gitlab.get_branches(repo.gitlab_project_id)
        return [b["name"] for b in branches]
    except Exception:
        return ["main", "develop"]


@router.get("/{repo_id}/gitlab-projects")
async def search_gitlab_projects(
    repo_id: str,
    search: str = "",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """搜索 GitLab 项目（用于选择器）"""
    result = await db.execute(select(Repo).where(Repo.id == repo_id))
    repo = result.scalars().first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")

    if not repo.access_token:
        raise HTTPException(status_code=400, detail="请先配置仓库访问令牌")

    try:
        gitlab = get_gitlab_service(repo.url, repo.access_token)
        projects = await gitlab.get_projects(search=search)
        return [{"id": p["id"], "name": p["name"], "path": p["path_with_namespace"]} for p in projects]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/{repo_id}/statistics")
async def get_repo_statistics(
    repo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取仓库统计信息"""
    result = await db.execute(select(Repo).where(Repo.id == repo_id))
    repo = result.scalars().first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")

    if not repo.access_token or not repo.gitlab_project_id:
        return {"message": "请先配置仓库访问令牌和项目 ID"}

    try:
        gitlab = get_gitlab_service(repo.url, repo.access_token)
        stats = await gitlab.get_project_statistics(repo.gitlab_project_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")
