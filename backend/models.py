from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# --- Enums ---
class WorkflowType(str, Enum):
    PROCURE = "PROCURE"
    RESCUE = "RESCUE"
    QUOTE = "QUOTE"
    SCHEDULE = "SCHEDULE"

class MissionStatus(str, Enum):
    CREATED = "CREATED"
    PLANNING = "PLANNING"
    DISCOVERING = "DISCOVERING"
    CALLING = "CALLING"
    ANALYZING = "ANALYZING"
    NEGOTIATING = "NEGOTIATING"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    CONFIRMING = "CONFIRMING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ABORTED = "ABORTED"

class CallStatus(str, Enum):
    QUEUED = "QUEUED"
    TALKING = "TALKING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    UNAVAILABLE = "UNAVAILABLE"

class OfferStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    BEST = "BEST"
    NEGOTIATING = "NEGOTIATING"
    REJECTED = "REJECTED"
    ACCEPTED = "ACCEPTED"

# --- SQLAlchemy ORM Models ---
class DBMission(Base):
    __tablename__ = "missions"

    id = Column(String, primary_key=True)
    objective = Column(Text, nullable=False)
    workflow_type = Column(String, default=WorkflowType.PROCURE.value)
    status = Column(String, default=MissionStatus.CREATED.value)
    item = Column(String, nullable=True)
    quantity = Column(Integer, nullable=True)
    target_budget = Column(Float, nullable=True)
    deadline = Column(String, nullable=True)
    location = Column(String, nullable=True)
    approval_threshold = Column(Float, default=5000.0)
    constraints = Column(JSON, default=dict)
    strategy = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    final_offer_id = Column(String, nullable=True)
    total_savings = Column(Float, default=0.0)
    summary_report = Column(JSON, nullable=True)

    calls = relationship("DBCallRecord", back_populates="mission", cascade="all, delete-orphan")
    offers = relationship("DBOffer", back_populates="mission", cascade="all, delete-orphan")
    events = relationship("DBTimelineEvent", back_populates="mission", cascade="all, delete-orphan")

class DBCallRecord(Base):
    __tablename__ = "call_records"

    id = Column(String, primary_key=True)
    mission_id = Column(String, ForeignKey("missions.id"), nullable=False)
    calle_call_id = Column(String, nullable=True)
    supplier_name = Column(String, nullable=False)
    supplier_phone = Column(String, nullable=False)
    call_type = Column(String, default="INQUIRY")  # INQUIRY, NEGOTIATION, CONFIRMATION
    status = Column(String, default=CallStatus.QUEUED.value)
    duration_seconds = Column(Integer, default=0)
    transcript_snippet = Column(Text, nullable=True)
    structured_result = Column(JSON, default=dict)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    mission = relationship("DBMission", back_populates="calls")

class DBOffer(Base):
    __tablename__ = "offers"

    id = Column(String, primary_key=True)
    mission_id = Column(String, ForeignKey("missions.id"), nullable=False)
    supplier_name = Column(String, nullable=False)
    supplier_phone = Column(String, nullable=False)
    contact_person = Column(String, nullable=True)
    unit_price = Column(Float, nullable=True)
    total_price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    negotiated_savings = Column(Float, default=0.0)
    quantity_available = Column(Integer, nullable=False)
    delivery_days = Column(Integer, nullable=True)
    delivery_date = Column(String, nullable=True)
    warranty_years = Column(Float, default=0.0)
    payment_terms = Column(String, nullable=True)
    composite_score = Column(Float, default=0.0)
    status = Column(String, default=OfferStatus.CANDIDATE.value)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    mission = relationship("DBMission", back_populates="offers")

class DBTimelineEvent(Base):
    __tablename__ = "timeline_events"

    id = Column(String, primary_key=True)
    mission_id = Column(String, ForeignKey("missions.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    metadata_json = Column(JSON, default=dict)

    mission = relationship("DBMission", back_populates="events")

# --- Pydantic Schemas ---
class MissionCreateRequest(BaseModel):
    objective: str = Field(..., description="High level natural language business objective")
    workflow_type: Optional[WorkflowType] = WorkflowType.PROCURE
    custom_budget: Optional[float] = None
    custom_deadline: Optional[str] = None
    approval_threshold: Optional[float] = 5000.0

class MissionBriefingUpdate(BaseModel):
    item: Optional[str] = None
    quantity: Optional[int] = None
    target_budget: Optional[float] = None
    deadline: Optional[str] = None
    approval_threshold: Optional[float] = None
    constraints: Optional[Dict[str, Any]] = None

class Supplier(BaseModel):
    id: str
    name: str
    phone: str
    category: str
    location: str
    products: List[str]
    price_range: Dict[str, float]
    typical_stock: int
    delivery_days_range: List[int]
    reliability_score: float = 0.90
    negotiable_tolerance: float = 0.15
    persona_notes: Optional[str] = None

class StructuredCallResult(BaseModel):
    availability: bool
    quantity_available: int = 0
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    delivery_days: Optional[int] = None
    warranty_years: Optional[float] = 0.0
    payment_terms: Optional[str] = "Standard"
    contact_person: Optional[str] = None
    negotiable: bool = False
    notes: Optional[str] = ""
    confidence: float = 1.0

class OfferDTO(BaseModel):
    id: str
    supplier_name: str
    supplier_phone: str
    contact_person: Optional[str] = None
    unit_price: Optional[float] = None
    total_price: float
    original_price: Optional[float] = None
    negotiated_savings: float = 0.0
    quantity_available: int
    delivery_days: Optional[int] = None
    delivery_date: Optional[str] = None
    warranty_years: float = 0.0
    payment_terms: Optional[str] = None
    composite_score: float = 0.0
    status: OfferStatus
    notes: Optional[str] = None

class CallRecordDTO(BaseModel):
    id: str
    calle_call_id: Optional[str] = None
    supplier_name: str
    supplier_phone: str
    call_type: str
    status: CallStatus
    duration_seconds: int
    transcript_snippet: Optional[str] = None
    structured_result: Dict[str, Any] = {}
    started_at: datetime

class TimelineEventDTO(BaseModel):
    id: str
    timestamp: datetime
    event_type: str
    title: str
    description: str
    metadata: Dict[str, Any] = {}

class MissionDTO(BaseModel):
    id: str
    objective: str
    workflow_type: WorkflowType
    status: MissionStatus
    item: Optional[str] = None
    quantity: Optional[int] = None
    target_budget: Optional[float] = None
    deadline: Optional[str] = None
    location: Optional[str] = None
    approval_threshold: float
    constraints: Dict[str, Any] = {}
    strategy: Dict[str, Any] = {}
    created_at: datetime
    completed_at: Optional[datetime] = None
    total_savings: float = 0.0
    summary_report: Optional[Dict[str, Any]] = None
    calls: List[CallRecordDTO] = []
    offers: List[OfferDTO] = []
    events: List[TimelineEventDTO] = []

class ApprovalDecisionRequest(BaseModel):
    decision: str = Field(..., description="'APPROVE', 'REJECT', or 'REQUEST_MORE'")
    notes: Optional[str] = None
