from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/")
async def get_roles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return []

@router.get("/{role_id}")
async def get_role(
    role_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return {}

@router.post("/")
async def create_role(
    role_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return role_data

@router.put("/{role_id}")
async def update_role(
    role_id: str,
    role_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return role_data

@router.delete("/{role_id}")
async def delete_role(
    role_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return {"message": "Role deleted"}