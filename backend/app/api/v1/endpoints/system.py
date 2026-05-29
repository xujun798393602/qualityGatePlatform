from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.core.config import get_settings
from app.models.user import User
from app.models.system_config import SystemConfig
from app.schemas.system import SystemConfigUpdate, SystemConfigResponse

router = APIRouter()
settings = get_settings()


@router.get("/config", response_model=SystemConfigResponse)
async def get_system_config(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Get all config from database
    result = await db.execute(select(SystemConfig))
    configs = {c.key: c.value for c in result.scalars().all()}
    return SystemConfigResponse(
        app_name=configs.get("app_name", settings.APP_NAME),
        app_version=configs.get("app_version", settings.APP_VERSION),
        jwt_expire_minutes=int(configs.get("jwt_expire_minutes", settings.ACCESS_TOKEN_EXPIRE_MINUTES)),
        max_login_attempts=int(configs.get("max_login_attempts", settings.MAX_LOGIN_ATTEMPTS)),
        lockout_duration_minutes=int(configs.get("lockout_duration_minutes", settings.LOCKOUT_DURATION_MINUTES)),
        debug=configs.get("debug", str(settings.DEBUG)).lower() == "true",
        gitlab_url=configs.get("gitlab_url"),
        gitlab_token=configs.get("gitlab_token"),
    )


@router.put("/config", response_model=SystemConfigResponse)
async def update_system_config(
    config_data: SystemConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Update config in database
    for key, value in config_data.model_dump(exclude_unset=True).items():
        if value is not None:
            result = await db.execute(select(SystemConfig).where(SystemConfig.key == key))
            config = result.scalars().first()
            if config:
                config.value = str(value)
            else:
                config = SystemConfig(key=key, value=str(value))
                db.add(config)
    await db.commit()
    # Return updated config
    return await get_system_config(db=db, current_user=current_user)
