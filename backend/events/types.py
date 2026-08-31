from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel

class EventType(str, Enum):
    AGENT_STATUS_CHANGED = "AGENT_STATUS_CHANGED"
    AGENT_REASONING = "AGENT_REASONING"
    CALL_STARTED = "CALL_STARTED"
    CALL_UPDATE = "CALL_UPDATE"
    CALL_COMPLETED = "CALL_COMPLETED"
    CALL_FAILED = "CALL_FAILED"
    OFFER_RECEIVED = "OFFER_RECEIVED"
    OFFERS_EVALUATED = "OFFERS_EVALUATED"
    NEGOTIATION_UPDATE = "NEGOTIATION_UPDATE"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    MISSION_COMPLETED = "MISSION_COMPLETED"
    MISSION_ABORTED = "MISSION_ABORTED"
    TIMELINE_EVENT = "TIMELINE_EVENT"

class MissionEvent(BaseModel):
    mission_id: str
    event_type: EventType
    title: str
    message: str
    data: Dict[str, Any] = {}
    timestamp: Optional[str] = None
