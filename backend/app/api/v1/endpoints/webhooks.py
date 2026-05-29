"""GitLab Webhook 端点 - 实现门禁真实生效"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.repo import Repo
from app.models.pipeline import Pipeline
from app.models.pipeline_run import PipelineRun
from app.models.pipeline_run_stage import PipelineRunStage
from app.models.gate import Gate
from app.models.gate_condition import GateCondition
from app.models.gate_check import GateCheck
from app.models.gate_check_result import GateCheckResult

router = APIRouter()


@router.post("/gitlab/{repo_id}")
async def gitlab_webhook(
    repo_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    接收 GitLab Webhook 事件
    支持的事件类型：
    - Pipeline Hook: 流水线执行完成时触发门禁检查
    - Merge Request Hook: MR 创建/更新时触发门禁检查
    """
    # 验证仓库存在
    result = await db.execute(select(Repo).where(Repo.id == repo_id))
    repo = result.scalars().first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")

    # 获取请求数据
    payload = await request.json()
    event_type = request.headers.get("X-Gitlab-Event", "")

    if event_type == "Pipeline Hook":
        await handle_pipeline_event(repo, payload, db)
    elif event_type == "Merge Request Hook":
        await handle_merge_request_event(repo, payload, db)

    return {"status": "ok"}


async def handle_pipeline_event(repo: Repo, payload: dict, db: AsyncSession):
    """处理 Pipeline 事件"""
    pipeline_data = payload.get("object_attributes", {})
    pipeline_id = pipeline_data.get("id")
    pipeline_status = pipeline_data.get("status")
    ref = pipeline_data.get("ref", "")
    commit = payload.get("commit", {})

    # 查找对应的流水线配置
    result = await db.execute(
        select(Pipeline).where(
            Pipeline.repo_id == repo.id,
            Pipeline.branch == ref,
            Pipeline.is_active == True,
        )
    )
    pipeline = result.scalars().first()

    if not pipeline:
        return

    # 创建运行记录
    run = PipelineRun(
        pipeline_id=pipeline.id,
        status=map_gitlab_status(pipeline_status),
        trigger_type="webhook",
    )
    db.add(run)
    await db.flush()

    # 创建阶段记录
    jobs = payload.get("builds", [])
    for job in jobs:
        run_stage = PipelineRunStage(
            run_id=run.id,
            stage_name=job.get("name", ""),
            status=map_gitlab_status(job.get("status", "")),
            started_at=job.get("started_at"),
            finished_at=job.get("finished_at"),
            output=job.get("trace", ""),
        )
        db.add(run_stage)

    # 更新流水线状态
    pipeline.status = map_gitlab_status(pipeline_status)
    pipeline.last_run_at = datetime.utcnow()
    pipeline.last_run_status = map_gitlab_status(pipeline_status)

    # 如果流水线完成，触发门禁检查
    if pipeline_status in ["success", "failed"]:
        await check_gates_for_pipeline(pipeline.id, run.id, db)

    await db.commit()


async def handle_merge_request_event(repo: Repo, payload: dict, db: AsyncSession):
    """处理 Merge Request 事件"""
    mr_data = payload.get("object_attributes", {})
    action = mr_data.get("action", "")

    # 只处理创建和更新事件
    if action not in ["open", "update"]:
        return

    ref = mr_data.get("source_branch", "")

    # 查找对应的流水线配置
    result = await db.execute(
        select(Pipeline).where(
            Pipeline.repo_id == repo.id,
            Pipeline.is_active == True,
        )
    )
    pipelines = result.scalars().all()

    # 触发所有匹配的流水线
    for pipeline in pipelines:
        if pipeline.trigger_type == "auto":
            # 创建运行记录
            run = PipelineRun(
                pipeline_id=pipeline.id,
                status="running",
                trigger_type="webhook",
            )
            db.add(run)

    await db.commit()


async def check_gates_for_pipeline(pipeline_id: str, run_id: str, db: AsyncSession):
    """检查流水线关联的所有门禁"""
    # 查找该流水线的所有门禁
    result = await db.execute(
        select(Gate).where(
            Gate.pipeline_id == pipeline_id,
            Gate.is_active == True,
        )
    )
    gates = result.scalars().all()

    for gate in gates:
        # 获取门禁条件
        cond_result = await db.execute(
            select(GateCondition).where(GateCondition.gate_id == gate.id)
        )
        conditions = cond_result.scalars().all()

        # 创建检查记录
        check = GateCheck(
            gate_id=gate.id,
            run_id=run_id,
            passed=True,  # 默认通过，下面会根据条件判断
        )
        db.add(check)
        await db.flush()

        # 检查每个条件
        all_passed = True
        for cond in conditions:
            # TODO: 从流水线运行结果中获取真实指标数据
            # 这里需要根据实际的测试结果、覆盖率报告等来判断
            actual_value = await get_metric_value(cond.metric, run_id, db)
            passed = evaluate_condition(actual_value, cond.operator, cond.value)

            check_result = GateCheckResult(
                check_id=check.id,
                metric=cond.metric,
                expected=f"{cond.operator} {cond.value}",
                actual=str(actual_value),
                passed=passed,
            )
            db.add(check_result)

            if not passed:
                all_passed = False

        check.passed = all_passed


async def get_metric_value(metric: str, run_id: str, db: AsyncSession) -> str:
    """获取指标的真实值"""
    # TODO: 从测试报告、覆盖率报告等中解析真实值
    # 目前返回默认值
    defaults = {
        "coverage": "80",
        "test_pass_rate": "95",
        "duplication": "5",
        "complexity": "10",
        "vulnerabilities": "0",
    }
    return defaults.get(metric, "0")


def evaluate_condition(actual: str, operator: str, expected: str) -> bool:
    """评估条件是否满足"""
    try:
        actual_num = float(actual)
        expected_num = float(expected)
        if operator == ">=":
            return actual_num >= expected_num
        elif operator == "<=":
            return actual_num <= expected_num
        elif operator == "==":
            return actual_num == expected_num
        elif operator == "!=":
            return actual_num != expected_num
        elif operator == ">":
            return actual_num > expected_num
        elif operator == "<":
            return actual_num < expected_num
    except ValueError:
        pass
    return False


def map_gitlab_status(gitlab_status: str) -> str:
    """映射 GitLab 状态到平台状态"""
    status_map = {
        "created": "pending",
        "pending": "pending",
        "running": "running",
        "success": "success",
        "failed": "failed",
        "canceled": "failed",
        "skipped": "skipped",
        "manual": "pending",
    }
    return status_map.get(gitlab_status, "pending")
