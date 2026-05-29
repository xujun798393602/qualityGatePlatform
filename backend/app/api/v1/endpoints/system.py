from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/config")
async def get_system_config(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return {}

@router.put("/config")
async def update_system_config(
    config_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return config_data