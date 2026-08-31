import pytest
from backend.models import WorkflowType, DBOffer, OfferStatus, DBCallRecord
from backend.agent.planner import mission_planner
from backend.services.discovery import discovery_service
from backend.agent.decision_engine import decision_engine
from backend.agent.approval_manager import approval_manager
from backend.calle.adapter import calle_adapter
from backend.agent.orchestrator import orchestrator
import datetime

def test_planner_procure_parsing():
    objective = "We need 500 ergonomic office chairs delivered to our Lahore office before Friday. Keep the total cost below $15,000."
    parsed = mission_planner.parse_objective(objective)
    
    assert parsed["quantity"] == 500
    assert parsed["target_budget"] == 15000.0
    assert "Lahore" in parsed["location"]
    assert "Friday" in parsed["deadline"]
    assert parsed["workflow_type"] == WorkflowType.PROCURE

def test_planner_rescue_parsing():
    objective = "Our delivery truck cancelled. Find a replacement that can arrive within two hours under $800."
    parsed = mission_planner.parse_objective(objective)
    assert parsed["workflow_type"] == WorkflowType.RESCUE
    assert parsed["target_budget"] == 800.0
    assert "2 hours" in parsed["deadline"] or "Immediate" in parsed["deadline"]

def test_planner_quote_parsing():
    objective = "I need a commercial 50kVA diesel generator. Collect competitive quotes under $20,000 with installation."
    parsed = mission_planner.parse_objective(objective)
    assert parsed["workflow_type"] == WorkflowType.QUOTE
    assert parsed["target_budget"] == 20000.0
    assert "Generator" in parsed["item"]

def test_planner_schedule_parsing():
    objective = "The 3 PM consultation appointment was cancelled. Call our priority waitlist to find someone who can take the slot."
    parsed = mission_planner.parse_objective(objective)
    assert parsed["workflow_type"] == WorkflowType.SCHEDULE
    assert "3:00 PM" in parsed["item"] or "Slot" in parsed["item"]

def test_supplier_discovery_all_workflows():
    # Procure
    procure_sup = discovery_service.discover_for_mission(WorkflowType.PROCURE, item="chairs", limit=4)
    assert len(procure_sup) >= 1
    assert any("XYZ" in s.name for s in procure_sup)
    
    # Rescue
    rescue_sup = discovery_service.discover_for_mission(WorkflowType.RESCUE, item="truck", limit=3)
    assert len(rescue_sup) >= 1
    assert any("Swift" in s.name for s in rescue_sup)
    
    # Quote
    quote_sup = discovery_service.discover_for_mission(WorkflowType.QUOTE, item="generator", limit=3)
    assert len(quote_sup) >= 1
    assert any("Voltech" in s.name for s in quote_sup)
    
    # Schedule
    schedule_sup = discovery_service.discover_for_mission(WorkflowType.SCHEDULE, item="slot", limit=3)
    assert len(schedule_sup) >= 1
    assert any("Sarah" in s.name for s in schedule_sup)

def test_decision_engine_evaluation():
    offers = [
        DBOffer(
            id="1",
            mission_id="m1",
            supplier_name="XYZ Supplies",
            supplier_phone="+123",
            total_price=13700.0,
            quantity_available=500,
            delivery_days=4,
            warranty_years=2.0
        ),
        DBOffer(
            id="2",
            mission_id="m1",
            supplier_name="ABC Furniture",
            supplier_phone="+124",
            total_price=15200.0,
            quantity_available=500,
            delivery_days=3,
            warranty_years=1.0
        ),
        DBOffer(
            id="3",
            mission_id="m1",
            supplier_name="MegaOffice",
            supplier_phone="+125",
            total_price=12500.0,
            quantity_available=250,  # Shortage
            delivery_days=2,
            warranty_years=1.0
        )
    ]
    
    evaluated, reasoning = decision_engine.evaluate_offers(offers, target_budget=15000.0, required_quantity=500)
    
    best = next(o for o in evaluated if o.status == OfferStatus.BEST.value)
    assert best.supplier_name == "XYZ Supplies"
    
    rejected = next(o for o in evaluated if o.supplier_name == "MegaOffice")
    assert rejected.status == OfferStatus.REJECTED.value

def test_approval_manager_threshold():
    offer_high = DBOffer(id="1", mission_id="m", supplier_name="X", supplier_phone="1", total_price=13700.0, quantity_available=500)
    offer_low = DBOffer(id="2", mission_id="m", supplier_name="Y", supplier_phone="2", total_price=450.0, quantity_available=10)
    
    assert approval_manager.requires_approval(offer_high, 5000.0) is True
    assert approval_manager.requires_approval(offer_low, 5000.0) is False

def test_orchestrator_serialization():
    call = DBCallRecord(
        id="c1",
        mission_id="m1",
        supplier_name="XYZ Supplies",
        supplier_phone="+12345",
        call_type="INQUIRY",
        status="TALKING",
        duration_seconds=0,
        started_at=datetime.datetime.utcnow()
    )
    d = orchestrator._call_to_dict(call)
    assert d["id"] == "c1"
    assert d["supplier_name"] == "XYZ Supplies"
    assert d["status"] == "TALKING"
    
    offer = DBOffer(
        id="o1",
        mission_id="m1",
        supplier_name="XYZ Supplies",
        supplier_phone="+12345",
        total_price=13700.0,
        quantity_available=500,
        status="BEST"
    )
    od = orchestrator._offer_to_dict(offer)
    assert od["id"] == "o1"
    assert od["total_price"] == 13700.0
    assert od["status"] == "BEST"

@pytest.mark.asyncio
async def test_calle_adapter_simulation():
    # Procure inquiry simulation
    res = await calle_adapter._execute_simulated_call(
        task="Call XYZ",
        result_schema={},
        metadata={"supplier_name": "XYZ Office Solutions", "call_type": "INQUIRY"}
    )
    assert res["status"] == "completed"
    assert res["result"]["availability"] is True
    assert res["result"]["total_price"] == 14700.0
    
    # Rescue simulation
    rescue_res = await calle_adapter._execute_simulated_call(
        task="Call Swift",
        result_schema={},
        metadata={"supplier_name": "Swift Logistics Express", "call_type": "RESCUE"}
    )
    assert rescue_res["status"] == "completed"
    assert rescue_res["result"]["service_available"] is True
    assert rescue_res["result"]["eta_minutes"] == 45
    
    # Quote simulation
    quote_res = await calle_adapter._execute_simulated_call(
        task="Call Voltech",
        result_schema={},
        metadata={"supplier_name": "Voltech Power Systems", "call_type": "QUOTE"}
    )
    assert quote_res["status"] == "completed"
    assert quote_res["result"]["total_price"] == 14200.0
    assert quote_res["result"]["warranty_years"] == 3.0
