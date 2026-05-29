from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, roles, teams, system

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(teams.router, prefix="/teams", tags=["Teams"])
api_router.include_router(system.router, prefix="/system", tags=["System"])