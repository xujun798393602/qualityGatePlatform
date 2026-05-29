from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.core.database import engine, Base
from app.api.v1.router import api_router

settings = get_settings()

@asynccontextmanager
async def lifespan(app):
    # 应用启动时初始化数据库
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # 初始化种子数据
    try:
        from app.core.seed_data import seed_database
        await seed_database()
        print("数据库初始化完成（可忽略）")
    except Exception as e:
        print(f"数据库初始化错误: {e}")
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}