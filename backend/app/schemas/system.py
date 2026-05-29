from typing import Optional, Dict, Any
from pydantic import BaseModel


class SystemConfigUpdate(BaseModel):
    app_name: Optional[str] = None
    app_version: Optional[str] = None
    jwt_expire_minutes: Optional[int] = None
    max_login_attempts: Optional[int] = None
    lockout_duration_minutes: Optional[int] = None
    debug: Optional[bool] = None
    gitlab_url: Optional[str] = None
    gitlab_token: Optional[str] = None


class SystemConfigResponse(BaseModel):
    app_name: str = "代码质量门禁管理平台"
    app_version: str = "0.1.0"
    jwt_expire_minutes: int = 30
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    debug: bool = False
    gitlab_url: Optional[str] = None
    gitlab_token: Optional[str] = None
