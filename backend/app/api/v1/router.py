from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, roles, teams, system, scripts, repos, pipelines, gates, webhooks, dashboard

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(teams.router, prefix="/teams", tags=["Teams"])
api_router.include_router(system.router, prefix="/system", tags=["System"])
api_router.include_router(scripts.router, prefix="/scripts", tags=["Scripts"])
api_router.include_router(repos.router, prefix="/repos", tags=["Repos"])
api_router.include_router(pipelines.router, prefix="/pipelines", tags=["Pipelines"])
api_router.include_router(gates.router, prefix="/gates", tags=["Gates"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
