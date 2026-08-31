import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.events.bus import event_bus
from backend.agent.orchestrator import orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])

@router.websocket("/ws/mission/{mission_id}")
async def mission_websocket(websocket: WebSocket, mission_id: str):
    await event_bus.connect(mission_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle incoming client messages e.g. approval, abort, pause
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
