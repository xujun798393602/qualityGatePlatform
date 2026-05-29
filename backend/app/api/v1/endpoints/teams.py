from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/")
async def get_teams(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return []

@router.get("/{team_id}")
async def get_team(
    team_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return {}

@router.post("/")
async def create_team(
    team_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return team_data

@router.put("/{team_id}")
async def update_team(
    team_id: str,
    team_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return team_data

@router.delete("/{team_id}")
async def delete_team(
    team_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return {"message": "Team deleted"}