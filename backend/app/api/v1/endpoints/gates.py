from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.models.gate import Gate
from app.models.gate_condition import GateCondition
from app.models.gate_check import GateCheck
from app.models.gate_check_result import GateCheckResult
from app.schemas.gate import GateCreate, GateUpdate, GateResponse, GateCheckResponse

router = APIRouter()


@router.get("/", response_model=List[GateResponse])
async def get_gates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Gate).where(Gate.is_active == True))
    gates = result.scalars().all()
    # Get conditions for each gate
    for gate in gates:
        cond_result = await db.execute(
            select(GateCondition).where(GateCondition.gate_id == gate.id)
        )
        gate.conditions = cond_result.scalars().all()
    return gates


@router.get("/{gate_id}", response_model=GateResponse)
async def get_gate(
    gate_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Gate).where(Gate.id == gate_id))
    gate = result.scalars().first()
    if not gate:
        raise HTTPException(status_code=404, detail="Gate not found")
    cond_result = await db.execute(
        select(GateCondition).where(GateCondition.gate_id == gate.id)
    )
    gate.conditions = cond_result.scalars().all()
    return gate


@router.post("/", response_model=GateResponse)
async def create_gate(
    gate_data: GateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    conditions_data = gate_data.conditions or []
    gate_dict = gate_data.model_dump(exclude={"conditions"})
    gate = Gate(**gate_dict, created_by=current_user.id)
    db.add(gate)
    await db.flush()
    # Create conditions
    for cond_data in conditions_data:
        condition = GateCondition(**cond_data.model_dump(), gate_id=gate.id)
        db.add(condition)
    await db.commit()
    await db.refresh(gate)
    cond_result = await db.execute(
        select(GateCondition).where(GateCondition.gate_id == gate.id)
    )
    gate.conditions = cond_result.scalars().all()
    return gate


@router.put("/{gate_id}", response_model=GateResponse)
async def update_gate(
    gate_id: str,
    gate_data: GateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Gate).where(Gate.id == gate_id))
    gate = result.scalars().first()
    if not gate:
        raise HTTPException(status_code=404, detail="Gate not found")
    conditions_data = gate_data.conditions
    update_dict = gate_data.model_dump(exclude_unset=True, exclude={"conditions"})
    for field, value in update_dict.items():
        setattr(gate, field, value)
    # Update conditions if provided
    if conditions_data is not None:
        # Delete old conditions
        old_conds = await db.execute(
            select(GateCondition).where(GateCondition.gate_id == gate.id)
        )
        for cond in old_conds.scalars().all():
            await db.delete(cond)
        # Create new conditions
        for cond_data in conditions_data:
            condition = GateCondition(**cond_data.model_dump(), gate_id=gate.id)
            db.add(condition)
    await db.commit()
    await db.refresh(gate)
    cond_result = await db.execute(
        select(GateCondition).where(GateCondition.gate_id == gate.id)
    )
    gate.conditions = cond_result.scalars().all()
    return gate


@router.delete("/{gate_id}")
async def delete_gate(
    gate_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Gate).where(Gate.id == gate_id))
    gate = result.scalars().first()
    if not gate:
        raise HTTPException(status_code=404, detail="Gate not found")
    gate.is_active = False
    await db.commit()
    return {"message": "Gate deleted"}


@router.post("/{gate_id}/check", response_model=GateCheckResponse)
async def check_gate(
    gate_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Gate).where(Gate.id == gate_id))
    gate = result.scalars().first()
    if not gate:
        raise HTTPException(status_code=404, detail="Gate not found")
    # Get conditions
    cond_result = await db.execute(
        select(GateCondition).where(GateCondition.gate_id == gate.id)
    )
    conditions = cond_result.scalars().all()
    # Create check record
    check = GateCheck(
        gate_id=gate_id,
        run_id=data.get("pipeline_run_id"),
        passed=True,
    )
    db.add(check)
    await db.flush()
    # Create check results (mock data for now)
    for cond in conditions:
        check_result = GateCheckResult(
            check_id=check.id,
            metric=cond.metric,
            expected=f"{cond.operator} {cond.value}",
            actual=cond.value,  # TODO: 获取真实数据
            passed=True,
        )
        db.add(check_result)
    await db.commit()
    return GateCheckResponse(
        id=check.id,
        gate_id=gate_id,
        gate_name=gate.name,
        passed=check.passed,
        checked_at=str(check.checked_at),
        conditions=[],
    )


@router.get("/{gate_id}/checks", response_model=List[GateCheckResponse])
async def get_gate_checks(
    gate_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(GateCheck).where(GateCheck.gate_id == gate_id).order_by(GateCheck.checked_at.desc())
    )
    checks = result.scalars().all()
    return [
        GateCheckResponse(
            id=c.id,
            gate_id=c.gate_id,
            passed=c.passed,
            checked_at=str(c.checked_at),
            conditions=[],
        )
        for c in checks
    ]
