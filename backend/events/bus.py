import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set
from fastapi import WebSocket
from backend.events.types import MissionEvent, EventType

logger = logging.getLogger(__name__)

class EventBus:
    """
    In-memory async pub/sub bus broadcasting real-time events to connected WebSocket clients per mission.
    """

    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, mission_id: str, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            if mission_id not in self._connections:
                self._connections[mission_id] = set()
            self._connections[mission_id].add(websocket)
        logger.info(f"WebSocket client connected to mission {mission_id}. Total: {len(self._connections[mission_id])}")

    async def disconnect(self, mission_id: str, websocket: WebSocket):
        async with self._lock:
            if mission_id in self._connections:
                self._connections[mission_id].discard(websocket)
                if not self._connections[mission_id]:
                    del self._connections[mission_id]
        logger.info(f"WebSocket client disconnected from mission {mission_id}")

    async def emit(self, event: MissionEvent):
        if not event.timestamp:
            event.timestamp = datetime.utcnow().isoformat()

        payload = event.dict()
        mission_id = event.mission_id

        async with self._lock:
            subscribers = list(self._connections.get(mission_id, []))

        if subscribers:
            json_str = json.dumps(payload)
            for ws in subscribers:
                try:
                    await ws.send_text(json_str)
                except Exception as e:
                    logger.warning(f"Failed to send event to WebSocket client: {e}")

event_bus = EventBus()
