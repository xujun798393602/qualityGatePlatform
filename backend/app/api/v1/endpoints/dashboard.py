"""仪表盘数据 API - 提供真实统计数据"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.pipeline import Pipeline
from app.models.pipeline_run import PipelineRun
from app.models.gate import Gate
from app.models.gate_check import GateCheck
from app.models.repo import Repo
from app.models.script import Script
from app.models.team import Team
from app.models.role import Role

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取仪表盘统计数据"""
    # 统计各模块数量
    user_count = (await db.execute(select(func.count(User.id)))).scalar() or 0
    team_count = (await db.execute(select(func.count(Team.id)).where(Team.is_active == True))).scalar() or 0
    role_count = (await db.execute(select(func.count(Role.id)).where(Role.is_active == True))).scalar() or 0
    script_count = (await db.execute(select(func.count(Script.id)).where(Script.is_active == True))).scalar() or 0
    repo_count = (await db.execute(select(func.count(Repo.id)).where(Repo.is_active == True))).scalar() or 0
    pipeline_count = (await db.execute(select(func.count(Pipeline.id)).where(Pipeline.is_active == True))).scalar() or 0
    gate_count = (await db.execute(select(func.count(Gate.id)).where(Gate.is_active == True))).scalar() or 0

    return {
        "user_count": user_count,
        "team_count": team_count,
        "role_count": role_count,
        "script_count": script_count,
        "repo_count": repo_count,
        "pipeline_count": pipeline_count,
        "gate_count": gate_count,
    }


@router.get("/pipeline-trend")
async def get_pipeline_trend(
    period: str = "week",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取流水线执行趋势数据"""
    now = datetime.utcnow()
    if period == "week":
        start_date = now - timedelta(days=7)
        group_format = "%Y-%m-%d"
    else:
        start_date = now - timedelta(days=30)
        group_format = "%Y-%m-%d"

    # 查询运行记录
    result = await db.execute(
        select(PipelineRun).where(PipelineRun.started_at >= start_date)
    )
    runs = result.scalars().all()

    # 按日期分组统计
    trend_data = {}
    for run in runs:
        date_str = run.started_at.strftime(group_format) if run.started_at else "unknown"
        if date_str not in trend_data:
            trend_data[date_str] = {"success": 0, "failed": 0, "running": 0}
        if run.status in trend_data[date_str]:
            trend_data[date_str][run.status] += 1

    # 生成日期列表
    dates = []
    current = start_date
    while current <= now:
        dates.append(current.strftime(group_format))
        current += timedelta(days=1)

    return {
        "dates": dates,
        "success": [trend_data.get(d, {}).get("success", 0) for d in dates],
        "failed": [trend_data.get(d, {}).get("failed", 0) for d in dates],
        "running": [trend_data.get(d, {}).get("running", 0) for d in dates],
    }


@router.get("/gate-pass-rate")
async def get_gate_pass_rate(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取门禁通过率数据"""
    result = await db.execute(select(GateCheck))
    checks = result.scalars().all()

    passed = sum(1 for c in checks if c.passed)
    failed = sum(1 for c in checks if not c.passed)
    total = len(checks)

    if total == 0:
        return {"passed": 0, "failed": 0, "rate": 0}

    return {
        "passed": passed,
        "failed": failed,
        "rate": round(passed / total * 100, 2),
    }


@router.get("/recent-pipelines")
async def get_recent_pipelines(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """获取最近的流水线运行记录"""
    result = await db.execute(
        select(PipelineRun).order_by(PipelineRun.started_at.desc()).limit(limit)
    )
    runs = result.scalars().all()

    # 获取流水线名称
    pipeline_ids = list(set(r.pipeline_id for r in runs))
    pipelines_result = await db.execute(
        select(Pipeline).where(Pipeline.id.in_(pipeline_ids))
    )
    pipelines_map = {p.id: p.name for p in pipelines_result.scalars().all()}

    return [
        {
            "id": run.id,
            "pipeline_name": pipelines_map.get(run.pipeline_id, "Unknown"),
            "status": run.status,
            "trigger_type": run.trigger_type,
            "started_at": run.started_at.isoformat() if run.started_at else None,
            "duration": run.duration,
        }
        for run in runs
    ]
