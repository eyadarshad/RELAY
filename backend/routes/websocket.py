import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.events.bus import event_bus
from backend.events.types import MissionEvent, EventType
from backend.database import async_session_factory
from backend.models import DBMission
from backend.routes.missions import _to_dto
from backend.agent.orchestrator import orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])

@router.websocket("/ws/mission/{mission_id}")
async def mission_websocket(websocket: WebSocket, mission_id: str):
    await event_bus.connect(mission_id, websocket)
    
    # Send initial state snapshot upon connection
    try:
        async with async_session_factory() as session:
            stmt = (
                select(DBMission)
                .options(
                    selectinload(DBMission.calls),
                    selectinload(DBMission.offers),
                    selectinload(DBMission.events)
                )
                .where(DBMission.id == mission_id)
            )
            res = await session.execute(stmt)
            m = res.scalar_one_or_none()
            if m:
                dto = _to_dto(m)
                await websocket.send_json({
                    "event_type": "STATE_SNAPSHOT",
                    "title": "State Sync",
                    "message": f"Connected to mission {mission_id}",
                    "data": dto.dict(),
                    "timestamp": dto.created_at.isoformat() if dto.created_at else None
                })
    except Exception as e:
        logger.warning(f"Could not send initial snapshot for mission {mission_id}: {e}")

    try:
        while True:
            data = await websocket.receive_json()
            # Handle incoming client messages e.g. approval, abort
            action = data.get("action")
            if action == "APPROVAL":
                decision = data.get("decision", "APPROVE")
                orchestrator.handle_approval_signal(mission_id, decision)
            elif action == "ABORT":
                orchestrator.abort_mission(mission_id)
    except WebSocketDisconnect:
        await event_bus.disconnect(mission_id, websocket)
    except Exception as e:
        logger.warning(f"WebSocket error for mission {mission_id}: {e}")
        await event_bus.disconnect(mission_id, websocket)
