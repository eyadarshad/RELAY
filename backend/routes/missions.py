import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.database import get_db_session
from backend.models import (
    DBMission, MissionCreateRequest, MissionBriefingUpdate,
    MissionDTO, ApprovalDecisionRequest, WorkflowType, MissionStatus
)
from backend.agent.planner import mission_planner
from backend.agent.orchestrator import orchestrator

router = APIRouter(prefix="/missions", tags=["Missions"])

@router.post("", response_model=MissionDTO)
async def create_mission(
    req: MissionCreateRequest,
    session: AsyncSession = Depends(get_db_session)
):
    """
    Creates and parses a new mission from high-level natural language prompt.
    """
    mission_id = f"msn_{uuid.uuid4().hex[:8]}"
    
    # Parse objective
    parsed = mission_planner.parse_objective(req.objective, req.workflow_type)
    
    # Allow user overrides from request if specified
    target_budget = req.custom_budget if req.custom_budget is not None else parsed["target_budget"]
    deadline = req.custom_deadline if req.custom_deadline is not None else parsed["deadline"]
    approval_threshold = req.approval_threshold if req.approval_threshold is not None else parsed["approval_threshold"]

    db_mission = DBMission(
        id=mission_id,
        objective=req.objective,
        workflow_type=(req.workflow_type or parsed["workflow_type"]).value,
        status=MissionStatus.CREATED.value,
        item=parsed["item"],
        quantity=parsed["quantity"],
        target_budget=target_budget,
        deadline=deadline,
        location=parsed["location"],
        approval_threshold=approval_threshold,
        constraints=parsed["constraints"],
        strategy=parsed["strategy"],
        created_at=datetime.utcnow()
    )

    session.add(db_mission)
    await session.commit()

    # Automatically trigger autonomous execution in background
    orchestrator.start_mission_in_background(mission_id)

    # Return full loaded DTO
    return await get_mission_by_id(mission_id, session)

@router.get("", response_model=List[MissionDTO])
async def list_missions(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session)
):
    stmt = (
        select(DBMission)
        .options(
            selectinload(DBMission.calls),
            selectinload(DBMission.offers),
            selectinload(DBMission.events)
        )
        .order_by(DBMission.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    missions = result.scalars().all()
    return [_to_dto(m) for m in missions]

@router.get("/{mission_id}", response_model=MissionDTO)
async def get_mission(
    mission_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    return await get_mission_by_id(mission_id, session)

async def get_mission_by_id(mission_id: str, session: AsyncSession) -> MissionDTO:
    stmt = (
        select(DBMission)
        .options(
            selectinload(DBMission.calls),
            selectinload(DBMission.offers),
            selectinload(DBMission.events)
        )
        .where(DBMission.id == mission_id)
    )
    result = await session.execute(stmt)
    mission = result.scalar_one_or_none()
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return _to_dto(mission)

@router.post("/{mission_id}/approval")
async def submit_approval_decision(
    mission_id: str,
    req: ApprovalDecisionRequest
):
    """
    Submits human approval decision: 'APPROVE', 'REJECT', or 'REQUEST_MORE'.
    """
    orchestrator.handle_approval_signal(mission_id, req.decision.upper())
    return {"status": "ok", "decision": req.decision.upper()}

@router.post("/{mission_id}/abort")
async def abort_mission(
    mission_id: str
):
    """
    Manually kills/aborts an ongoing mission.
    """
    orchestrator.abort_mission(mission_id)
    return {"status": "aborted", "mission_id": mission_id}

def _to_dto(m: DBMission) -> MissionDTO:
    return MissionDTO(
        id=m.id,
        objective=m.objective,
        workflow_type=WorkflowType(m.workflow_type),
        status=MissionStatus(m.status),
        item=m.item,
        quantity=m.quantity,
        target_budget=m.target_budget,
        deadline=m.deadline,
        location=m.location,
        approval_threshold=m.approval_threshold or 5000.0,
        constraints=m.constraints or {},
        strategy=m.strategy or {},
        created_at=m.created_at,
        completed_at=m.completed_at,
        total_savings=m.total_savings or 0.0,
        summary_report=m.summary_report,
        calls=[
            {
                "id": c.id,
                "calle_call_id": c.calle_call_id,
                "supplier_name": c.supplier_name,
                "supplier_phone": c.supplier_phone,
                "call_type": c.call_type,
                "status": c.status,
                "duration_seconds": c.duration_seconds or 0,
                "transcript_snippet": c.transcript_snippet,
                "structured_result": c.structured_result or {},
                "started_at": c.started_at
            }
            for c in (m.calls or [])
        ],
        offers=[
            {
                "id": o.id,
                "supplier_name": o.supplier_name,
                "supplier_phone": o.supplier_phone,
                "contact_person": o.contact_person,
                "unit_price": o.unit_price,
                "total_price": o.total_price,
                "original_price": o.original_price,
                "negotiated_savings": o.negotiated_savings,
                "quantity_available": o.quantity_available,
                "delivery_days": o.delivery_days,
                "delivery_date": o.delivery_date,
                "warranty_years": o.warranty_years,
                "payment_terms": o.payment_terms,
                "composite_score": o.composite_score,
                "status": o.status,
                "notes": o.notes
            }
            for o in (m.offers or [])
        ],
        events=[
            {
                "id": e.id,
                "timestamp": e.timestamp,
                "event_type": e.event_type,
                "title": e.title,
                "description": e.description,
                "metadata": e.metadata_json or {}
            }
            for e in (m.events or [])
        ]
    )
