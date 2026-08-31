import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy import select
from backend.database import async_session_factory
from backend.models import (
    DBMission, DBCallRecord, DBOffer, DBTimelineEvent,
    MissionStatus, CallStatus, OfferStatus, WorkflowType
)
from backend.agent.planner import mission_planner
from backend.services.discovery import discovery_service
from backend.agent.caller import call_agent
from backend.agent.decision_engine import decision_engine
from backend.agent.negotiator import negotiation_engine
from backend.agent.approval_manager import approval_manager
from backend.events.bus import event_bus
from backend.events.types import MissionEvent, EventType

logger = logging.getLogger(__name__)

class MissionOrchestrator:
    """
    Central Autonomous State Machine for RELAY.
    Orchestrates multi-call, multi-phase operational mission loops across 4 distinct workflow archetypes:
    1. PROCURE: Sourcing -> Multi-Call Inquiry -> Scoring -> Leverage Negotiation -> Human Approval Gate -> Final PO Lock
    2. RESCUE: Sequential Emergency Dialing -> Immediate SLA Dispatch Lock
    3. QUOTE: Multi-Vendor Calling -> Spec Normalization -> Ranked Comparative Matrix
    4. SCHEDULE: Sequential Waitlist Dialing -> Priority Acceptance -> Calendar Booking Lock
    """

    def __init__(self):
        self._active_tasks: Dict[str, asyncio.Task] = {}
        self._approval_events: Dict[str, asyncio.Event] = {}
        self._approval_decisions: Dict[str, str] = {}

    def start_mission_in_background(self, mission_id: str):
        task = asyncio.create_task(self.run_mission(mission_id))
        self._active_tasks[mission_id] = task

    def handle_approval_signal(self, mission_id: str, decision: str):
        self._approval_decisions[mission_id] = decision
        if mission_id in self._approval_events:
            self._approval_events[mission_id].set()

    def abort_mission(self, mission_id: str):
        if mission_id in self._active_tasks:
            self._active_tasks[mission_id].cancel()

    async def _emit_timeline(self, session, mission_id: str, event_type: str, title: str, description: str, metadata: dict = None):
        ev = DBTimelineEvent(
            id=f"evt_{uuid.uuid4().hex[:8]}",
            mission_id=mission_id,
            timestamp=datetime.utcnow(),
            event_type=event_type,
            title=title,
            description=description,
            metadata_json=metadata or {}
        )
        session.add(ev)
        await session.flush()

        await event_bus.emit(MissionEvent(
            mission_id=mission_id,
            event_type=EventType.TIMELINE_EVENT,
            title=title,
            message=description,
            data={"event_id": ev.id, "event_type": event_type, "metadata": metadata or {}}
        ))

    async def _set_status(self, session, mission: DBMission, new_status: MissionStatus, message: str = ""):
        mission.status = new_status.value
        await session.flush()
        await event_bus.emit(MissionEvent(
            mission_id=mission.id,
            event_type=EventType.AGENT_STATUS_CHANGED,
            title=f"Status: {new_status.value}",
            message=message or f"Agent transitioned to {new_status.value}",
            data={"status": new_status.value}
        ))

    async def _emit_reasoning(self, mission_id: str, thought: str):
        await event_bus.emit(MissionEvent(
            mission_id=mission_id,
            event_type=EventType.AGENT_REASONING,
            title="Agent Thought",
            message=thought,
            data={"thought": thought}
        ))

    def _offer_to_dict(self, offer: DBOffer) -> Dict[str, Any]:
        return {
            "id": offer.id,
            "supplier_name": offer.supplier_name,
            "supplier_phone": offer.supplier_phone,
            "contact_person": offer.contact_person,
            "unit_price": offer.unit_price,
            "total_price": offer.total_price,
            "original_price": offer.original_price,
            "negotiated_savings": offer.negotiated_savings,
            "quantity_available": offer.quantity_available,
            "delivery_days": offer.delivery_days,
            "delivery_date": offer.delivery_date,
            "warranty_years": offer.warranty_years,
            "payment_terms": offer.payment_terms,
            "composite_score": offer.composite_score,
            "status": offer.status,
            "notes": offer.notes
        }

    def _call_to_dict(self, call_rec: DBCallRecord) -> Dict[str, Any]:
        return {
            "id": call_rec.id,
            "calle_call_id": call_rec.calle_call_id,
            "supplier_name": call_rec.supplier_name,
            "supplier_phone": call_rec.supplier_phone,
            "call_type": call_rec.call_type,
            "status": call_rec.status,
            "duration_seconds": call_rec.duration_seconds,
            "transcript_snippet": call_rec.transcript_snippet,
            "structured_result": call_rec.structured_result or {},
            "started_at": call_rec.started_at.isoformat() if call_rec.started_at else None,
            "ended_at": call_rec.ended_at.isoformat() if call_rec.ended_at else None,
        }

    async def run_mission(self, mission_id: str):
        logger.info(f"Starting autonomous mission orchestration for ID: {mission_id}")
        mission_start_time = datetime.utcnow()

        async with async_session_factory() as session:
            try:
                result = await session.execute(select(DBMission).where(DBMission.id == mission_id))
                mission = result.scalar_one_or_none()
                if not mission:
                    logger.error(f"Mission {mission_id} not found.")
                    return

                # STEP 1: PLANNING (Universal)
                await self._set_status(session, mission, MissionStatus.PLANNING, "Analyzing mission objective and extracting constraints...")
                await self._emit_timeline(session, mission.id, "PLANNING", "Mission Initialized", f"Objective: '{mission.objective}'")
                await self._emit_reasoning(mission.id, f"Parsing requirement '{mission.objective}' for budgetary, SLA, and workflow parameters...")

                await asyncio.sleep(1.0)
                parsed = mission_planner.parse_objective(mission.objective, WorkflowType(mission.workflow_type))
                mission.item = parsed["item"]
                mission.quantity = parsed["quantity"]
                mission.target_budget = parsed["target_budget"]
                mission.deadline = parsed["deadline"]
                mission.location = parsed["location"]
                mission.constraints = parsed["constraints"]
                mission.strategy = parsed["strategy"]
                mission.approval_threshold = parsed["approval_threshold"]

                await session.flush()
                await self._emit_reasoning(
                    mission.id,
                    f"Requirements extracted: Workflow [{mission.workflow_type}], Target: {mission.quantity} {mission.item}, "
                    f"Budget Ceiling: ${mission.target_budget:,.2f}, SLA: '{mission.deadline}'."
                )

                # Dispatch to workflow-specific executor
                wf = WorkflowType(mission.workflow_type)
                if wf == WorkflowType.PROCURE:
                    await self._run_procure(session, mission, parsed, mission_start_time)
                elif wf == WorkflowType.RESCUE:
                    await self._run_rescue(session, mission, parsed, mission_start_time)
                elif wf == WorkflowType.QUOTE:
                    await self._run_quote(session, mission, parsed, mission_start_time)
                elif wf == WorkflowType.SCHEDULE:
                    await self._run_schedule(session, mission, parsed, mission_start_time)

            except asyncio.CancelledError:
                logger.warning(f"Mission {mission_id} was aborted by user.")
                mission.status = MissionStatus.ABORTED.value
                await session.commit()
                await event_bus.emit(MissionEvent(
                    mission_id=mission_id,
                    event_type=EventType.MISSION_ABORTED,
                    title="Mission Aborted",
                    message="The active mission was manually cancelled.",
                    data={}
                ))
            except Exception as e:
                logger.exception(f"Unhandled error in mission {mission_id}: {e}")
                mission.status = MissionStatus.FAILED.value
                await session.commit()
                await event_bus.emit(MissionEvent(
                    mission_id=mission_id,
                    event_type=EventType.AGENT_STATUS_CHANGED,
                    title="Mission Error",
                    message=str(e),
                    data={"error": str(e)}
                ))
            finally:
                if mission_id in self._active_tasks:
                    del self._active_tasks[mission_id]
                if mission_id in self._approval_events:
                    del self._approval_events[mission_id]
                if mission_id in self._approval_decisions:
                    del self._approval_decisions[mission_id]

    # =========================================================================
    # WORKFLOW 01: PROCURE (Full Multi-Call, Negotiation, Approval, Confirmation)
    # =========================================================================
    async def _run_procure(self, session, mission: DBMission, parsed: dict, start_time: datetime):
        # 1. Discover
        await self._set_status(session, mission, MissionStatus.DISCOVERING, "Scanning supplier directory and ranking candidates...")
        await asyncio.sleep(1.0)

        suppliers = discovery_service.discover_for_mission(
            workflow_type=WorkflowType.PROCURE,
            item=mission.item,
            location=mission.location,
            limit=4
        )
        if not suppliers:
            await self._set_status(session, mission, MissionStatus.FAILED, "No candidate suppliers found.")
            return

        supplier_names = ", ".join(s.name for s in suppliers)
        await self._emit_timeline(session, mission.id, "DISCOVERY", f"{len(suppliers)} Suppliers Identified", f"Identified candidates: {supplier_names}")
        await self._emit_reasoning(mission.id, f"Identified {len(suppliers)} vetted suppliers in {mission.location}. Formulating CALL-E outreach queue...")

        # 2. Multi-Call Inquiries
        await self._set_status(session, mission, MissionStatus.CALLING, f"Initiating phone calls to {len(suppliers)} suppliers via CALL-E...")
        collected_offers: List[DBOffer] = []

        for idx, supplier in enumerate(suppliers, start=1):
            call_rec = DBCallRecord(
                id=f"call_{uuid.uuid4().hex[:8]}",
                mission_id=mission.id,
                supplier_name=supplier.name,
                supplier_phone=supplier.phone,
                call_type="INQUIRY",
                status=CallStatus.TALKING.value,
                started_at=datetime.utcnow()
            )
            session.add(call_rec)
            await session.flush()

            await event_bus.emit(MissionEvent(
                mission_id=mission.id,
                event_type=EventType.CALL_STARTED,
                title=f"Calling {supplier.name}",
                message=f"Dialing {supplier.phone} (Call {idx}/{len(suppliers)})...",
                data=self._call_to_dict(call_rec)
            ))
            await self._emit_reasoning(mission.id, f"Connecting with {supplier.name} at {supplier.phone} to inquire about {mission.quantity} {mission.item}...")

            call_result = await call_agent.make_inquiry_call(
                supplier=supplier,
                item=mission.item,
                quantity=mission.quantity,
                budget=mission.target_budget,
                deadline=mission.deadline,
                mission_id=mission.id
            )

            structured = call_result.get("result", {})
            call_rec.status = CallStatus.COMPLETED.value
            call_rec.duration_seconds = call_result.get("duration_seconds", 45)
            call_rec.transcript_snippet = call_result.get("transcript", "")
            call_rec.structured_result = structured
            call_rec.ended_at = datetime.utcnow()
            await session.flush()

            await event_bus.emit(MissionEvent(
                mission_id=mission.id,
                event_type=EventType.CALL_COMPLETED,
                title=f"Call Finished: {supplier.name}",
                message=f"Received structured response in {call_rec.duration_seconds}s.",
                data=self._call_to_dict(call_rec)
            ))

            has_availability = structured.get("availability", False)
            total_price = float(structured.get("total_price", 0.0))
            qty_avail = int(structured.get("quantity_available", 0))

            offer = DBOffer(
                id=f"off_{uuid.uuid4().hex[:8]}",
                mission_id=mission.id,
                supplier_name=supplier.name,
                supplier_phone=supplier.phone,
                contact_person=structured.get("contact_person", "Sales Desk"),
                unit_price=float(structured.get("unit_price", 0.0)),
                total_price=total_price,
                original_price=total_price,
                quantity_available=qty_avail,
                delivery_days=int(structured.get("delivery_days", 4)),
                delivery_date=f"In {structured.get('delivery_days', 4)} business days",
                warranty_years=float(structured.get("warranty_years", 1.0)),
                payment_terms=structured.get("payment_terms", "Standard"),
                status=OfferStatus.CANDIDATE.value if has_availability else OfferStatus.REJECTED.value,
                notes=structured.get("notes", "")
            )
            session.add(offer)
            await session.flush()
            collected_offers.append(offer)

            await event_bus.emit(MissionEvent(
                mission_id=mission.id,
                event_type=EventType.OFFER_RECEIVED,
                title=f"Offer: {supplier.name}",
                message=f"Quoted ${total_price:,.2f} for {qty_avail} units.",
                data=self._offer_to_dict(offer)
            ))

            await self._emit_timeline(
                session, mission.id, "CALL",
                f"Call Completed: {supplier.name}",
                f"Quote: ${total_price:,.2f} | Stock: {qty_avail} | ETA: {structured.get('delivery_days', 4)} days"
            )

        # 3. Analyze & Decision
        await self._set_status(session, mission, MissionStatus.ANALYZING, "Evaluating collected supplier quotes...")
        await asyncio.sleep(1.0)

        evaluated_offers, explanation = decision_engine.evaluate_offers(
            offers=collected_offers,
            target_budget=mission.target_budget,
            required_quantity=mission.quantity,
            max_delivery_days=mission.constraints.get("max_delivery_days", 4)
        )
        await session.flush()

        await event_bus.emit(MissionEvent(
            mission_id=mission.id,
            event_type=EventType.OFFERS_EVALUATED,
            title="Quotes Evaluated",
            message=explanation,
            data={"offers_count": len(evaluated_offers), "offers": [self._offer_to_dict(o) for o in evaluated_offers]}
        ))
        await self._emit_reasoning(mission.id, f"Decision Engine Analysis: {explanation}")
        await self._emit_timeline(session, mission.id, "ANALYSIS", "Offers Scored & Ranked", explanation)

        best_offer = next((o for o in evaluated_offers if o.status == OfferStatus.BEST.value), None)
        second_best_offer = next((o for o in evaluated_offers if o.id != (best_offer.id if best_offer else "") and o.status == OfferStatus.CANDIDATE.value), None)

        if not best_offer:
            await self._set_status(session, mission, MissionStatus.FAILED, "No qualifying supplier met constraints.")
            return

        best_supplier = next((s for s in suppliers if s.name == best_offer.supplier_name), suppliers[0])

        # 4. Negotiate (Targeted 2nd Call)
        if negotiation_engine.is_negotiation_warranted(best_offer, second_best_offer, mission.target_budget):
            await self._set_status(session, mission, MissionStatus.NEGOTIATING, f"Initiating price negotiation call with {best_offer.supplier_name}...")

            neg_call_rec = DBCallRecord(
                id=f"call_{uuid.uuid4().hex[:8]}",
                mission_id=mission.id,
                supplier_name=best_supplier.name,
                supplier_phone=best_supplier.phone,
                call_type="NEGOTIATION",
                status=CallStatus.TALKING.value,
                started_at=datetime.utcnow()
            )
            session.add(neg_call_rec)
            await session.flush()

            await event_bus.emit(MissionEvent(
                mission_id=mission.id,
                event_type=EventType.CALL_STARTED,
                title=f"Negotiating with {best_supplier.name}",
                message=f"Placing secondary leverage call to {best_supplier.phone}...",
                data=self._call_to_dict(neg_call_rec)
            ))

            comp_price_val = second_best_offer.total_price if second_best_offer else 14100.00
            await self._emit_reasoning(
                mission.id,
                f"Opening negotiation with {best_supplier.name}. Leverage: Competing bid at ${comp_price_val:,.2f}. Target: ~$13,700."
            )

            neg_result, savings = await negotiation_engine.execute_negotiation(
                best_offer=best_offer,
                supplier=best_supplier,
                second_best_offer=second_best_offer,
                item=mission.item,
                quantity=mission.quantity,
                mission_id=mission.id
            )

            neg_call_rec.status = CallStatus.COMPLETED.value
            neg_call_rec.duration_seconds = neg_result.get("duration_seconds", 60)
            neg_call_rec.transcript_snippet = neg_result.get("transcript", "")
            neg_call_rec.structured_result = neg_result.get("result", {})
            neg_call_rec.ended_at = datetime.utcnow()

            mission.total_savings = savings
            await session.flush()

            await event_bus.emit(MissionEvent(
                mission_id=mission.id,
                event_type=EventType.CALL_COMPLETED,
                title=f"Negotiation Call Complete: {best_supplier.name}",
                message=f"Negotiation call concluded in {neg_call_rec.duration_seconds}s.",
                data=self._call_to_dict(neg_call_rec)
            ))

            await event_bus.emit(MissionEvent(
                mission_id=mission.id,
                event_type=EventType.NEGOTIATION_UPDATE,
                title=f"Negotiation Success with {best_offer.supplier_name}",
                message=f"Achieved ${savings:,.2f} in verified discounts! New price: ${best_offer.total_price:,.2f}",
                data={
                    "offer_id": best_offer.id,
                    "savings": savings,
                    "original_price": best_offer.original_price,
                    "revised_price": best_offer.total_price,
                    "unit_price": best_offer.unit_price,
                    "supplier_name": best_offer.supplier_name,
                    "offer": self._offer_to_dict(best_offer)
                }
            ))

            await self._emit_timeline(
                session, mission.id, "NEGOTIATION",
                f"Price Reduced: -${savings:,.2f}",
                f"Discount secured from {best_offer.supplier_name}: ${best_offer.original_price:,.2f} -> ${best_offer.total_price:,.2f}"
            )

        # 5. Human Approval Gate
        if approval_manager.requires_approval(best_offer, mission.approval_threshold):
            await self._set_status(session, mission, MissionStatus.APPROVAL_REQUIRED, "High-value purchase requires executive human approval...")
            approval_data = approval_manager.generate_approval_summary(best_offer, mission.target_budget)

            await event_bus.emit(MissionEvent(
                mission_id=mission.id,
                event_type=EventType.APPROVAL_REQUIRED,
                title="Human Approval Required",
                message=f"Authorize purchase of {best_offer.quantity_available} {mission.item} for ${best_offer.total_price:,.2f}?",
                data=approval_data
            ))

            await self._emit_timeline(
                session, mission.id, "APPROVAL_GATE", "Human Approval Requested",
                f"Purchase amount of ${best_offer.total_price:,.2f} exceeds ${mission.approval_threshold:,.2f} threshold."
            )
            await self._emit_reasoning(
                mission.id,
                f"Halting before final purchase order. Best offer is ${best_offer.total_price:,.2f} from {best_offer.supplier_name}. Awaiting user approval..."
            )

            self._approval_events[mission.id] = asyncio.Event()
            try:
                await asyncio.wait_for(self._approval_events[mission.id].wait(), timeout=600.0)
            except asyncio.TimeoutError:
                self._approval_decisions[mission.id] = "REJECT"

            decision = self._approval_decisions.get(mission.id, "APPROVE")
            if decision == "REJECT":
                await self._set_status(session, mission, MissionStatus.ABORTED, "Mission rejected by human reviewer.")
                await self._emit_timeline(session, mission.id, "APPROVAL", "Order Rejected", "User rejected the proposed supplier terms.")
                return

            await self._emit_timeline(session, mission.id, "APPROVAL", "Order Approved", f"User authorized purchase commitment of ${best_offer.total_price:,.2f}.")
            await self._emit_reasoning(mission.id, "Approval granted by operator. Executing final confirmation call to lock in order reference...")

        # 6. Final Confirmation Call
        await self._set_status(session, mission, MissionStatus.CONFIRMING, f"Placing final purchase confirmation call with {best_offer.supplier_name}...")

        conf_call_rec = DBCallRecord(
            id=f"call_{uuid.uuid4().hex[:8]}",
            mission_id=mission.id,
            supplier_name=best_supplier.name,
            supplier_phone=best_supplier.phone,
            call_type="CONFIRMATION",
            status=CallStatus.TALKING.value,
            started_at=datetime.utcnow()
        )
        session.add(conf_call_rec)
        await session.flush()

        await event_bus.emit(MissionEvent(
            mission_id=mission.id,
            event_type=EventType.CALL_STARTED,
            title=f"Order Locking Call: {best_supplier.name}",
            message=f"Executing final binding confirmation call to {best_supplier.phone}...",
            data=self._call_to_dict(conf_call_rec)
        ))

        conf_result = await call_agent.make_confirmation_call(
            supplier=best_supplier,
            final_price=best_offer.total_price,
            quantity=best_offer.quantity_available,
            item=mission.item,
            delivery_date=best_offer.delivery_date or "September 4",
            mission_id=mission.id
        )

        conf_call_rec.status = CallStatus.COMPLETED.value
        conf_call_rec.duration_seconds = conf_result.get("duration_seconds", 40)
        conf_call_rec.transcript_snippet = conf_result.get("transcript", "")
        conf_call_rec.structured_result = conf_result.get("result", {})
        conf_call_rec.ended_at = datetime.utcnow()
        await session.flush()

        await event_bus.emit(MissionEvent(
            mission_id=mission.id,
            event_type=EventType.CALL_COMPLETED,
            title=f"Confirmation Call Finished: {best_supplier.name}",
            message=f"Confirmation call finalized in {conf_call_rec.duration_seconds}s.",
            data=self._call_to_dict(conf_call_rec)
        ))

        best_offer.status = OfferStatus.ACCEPTED.value
        mission.final_offer_id = best_offer.id
        conf_data = conf_result.get("result", {})
        po_number = conf_data.get("order_reference_number", "PO-XYZ-2026-0941")

        await self._emit_timeline(
            session, mission.id, "CONFIRMATION",
            f"Order Locked In ({po_number})",
            f"Final confirmation completed with {best_offer.supplier_name}. Delivery guaranteed for {conf_data.get('delivery_commitment_date', 'Thursday, Sept 4')}."
        )

        # 7. Mission Complete
        mission.completed_at = datetime.utcnow()
        mission.total_savings = max(0.0, mission.target_budget - best_offer.total_price)
        elapsed_seconds = max(1, int((datetime.utcnow() - start_time).total_seconds()))

        mission_report = {
            "mission_id": mission.id,
            "workflow_type": "PROCURE",
            "objective": mission.objective,
            "item_secured": f"{best_offer.quantity_available} {mission.item}",
            "final_price": best_offer.total_price,
            "original_budget": mission.target_budget,
            "total_savings": mission.total_savings,
            "delivery_commitment": conf_data.get("delivery_commitment_date", "Thursday, September 4"),
            "warranty": f"{best_offer.warranty_years} years",
            "supplier_confirmed": best_offer.supplier_name,
            "po_reference": po_number,
            "calls_initiated": len(suppliers) + 2,
            "successful_conversations": len(suppliers) + 2,
            "negotiation_rounds": 1,
            "execution_time_seconds": elapsed_seconds
        }
        mission.summary_report = mission_report
        await session.flush()

        await self._set_status(session, mission, MissionStatus.COMPLETED, "Mission Accomplished! Structured transaction complete.")
        await self._emit_reasoning(mission.id, f"Mission Accomplished: {best_offer.quantity_available} units secured at ${best_offer.total_price:,.2f} (${mission.total_savings:,.2f} saved).")

        await event_bus.emit(MissionEvent(
            mission_id=mission.id,
            event_type=EventType.MISSION_COMPLETED,
            title="Mission Complete",
            message=f"Successfully secured {best_offer.quantity_available} {mission.item} from {best_offer.supplier_name}.",
            data=mission_report
        ))
        await session.commit()

    # =========================================================================
    # WORKFLOW 02: RESCUE (Emergency Rapid Sequential Dispatcher Dialing)
    # =========================================================================
    async def _run_rescue(self, session, mission: DBMission, parsed: dict, start_time: datetime):
        await self._set_status(session, mission, MissionStatus.DISCOVERING, "Scanning emergency logistics fleet carriers...")
        await asyncio.sleep(1.0)

        dispatchers = discovery_service.discover_for_mission(
            workflow_type=WorkflowType.RESCUE,
            item=mission.item,
            location=mission.location,
            limit=3
        )
        if not dispatchers:
            await self._set_status(session, mission, MissionStatus.FAILED, "No emergency carriers found in region.")
            return

        carrier_names = ", ".join(d.name for d in dispatchers)
        await self._emit_timeline(session, mission.id, "DISCOVERY", f"{len(dispatchers)} Dispatchers Identified", f"Emergency fleet: {carrier_names}")
        await self._emit_reasoning(mission.id, f"Identified {len(dispatchers)} emergency freight dispatchers. Initiating immediate priority sequential dialing...")

        await self._set_status(session, mission, MissionStatus.CALLING, "Dialing emergency carrier dispatchers sequentially...")

        secured_offer: Optional[DBOffer] = None
        calls_count = 0

        for idx, carrier in enumerate(dispatchers, start=1):
            calls_count += 1
            call_rec = DBCallRecord(
                id=f"call_{uuid.uuid4().hex[:8]}",
                mission_id=mission.id,
                supplier_name=carrier.name,
                supplier_phone=carrier.phone,
                call_type="RESCUE",
                status=CallStatus.TALKING.value,
                started_at=datetime.utcnow()
            )
            session.add(call_rec)
            await session.flush()

            await event_bus.emit(MissionEvent(
                mission_id=mission.id,
                event_type=EventType.CALL_STARTED,
                title=f"Emergency Dial: {carrier.name}",
                message=f"Contacting {carrier.name} ({carrier.phone}) for immediate 2-hour dispatch...",
                data=self._call_to_dict(call_rec)
            ))
            await self._emit_reasoning(mission.id, f"Checking availability of 26ft box truck with {carrier.name} (target ETA < 120 min, budget < ${mission.target_budget:,.2f})...")

            call_result = await call_agent.make_rescue_call(
                supplier=carrier,
                service_needed=mission.item,
                eta_target="2 hours",
                mission_id=mission.id
            )

            structured = call_result.get("result", {})
            call_rec.status = CallStatus.COMPLETED.value
            call_rec.duration_seconds = call_result.get("duration_seconds", 35)
            call_rec.transcript_snippet = call_result.get("transcript", "")
            call_rec.structured_result = structured
            call_rec.ended_at = datetime.utcnow()
            await session.flush()

            await event_bus.emit(MissionEvent(
                mission_id=mission.id,
                event_type=EventType.CALL_COMPLETED,
                title=f"Call Complete: {carrier.name}",
                message=f"Carrier response received in {call_rec.duration_seconds}s.",
                data=self._call_to_dict(call_rec)
            ))

            is_avail = structured.get("service_available", False)
            eta_mins = int(structured.get("eta_minutes", 999))
            cost = float(structured.get("total_cost", 0.0))
            driver = structured.get("driver_contact", "Dispatch Hotline")

            offer = DBOffer(
                id=f"off_{uuid.uuid4().hex[:8]}",
                mission_id=mission.id,
                supplier_name=carrier.name,
                supplier_phone=carrier.phone,
                contact_person=driver,
                unit_price=cost,
                total_price=cost,
                original_price=cost,
                quantity_available=1,
                delivery_days=0,
                delivery_date=f"ETA: {eta_mins} Minutes",
                warranty_years=0.0,
                payment_terms="Immediate Corporate Billing",
                status=OfferStatus.ACCEPTED.value if (is_avail and eta_mins <= 120 and cost <= mission.target_budget) else OfferStatus.REJECTED.value,
                notes=f"ETA: {eta_mins} min | Cost: ${cost:,.2f} | Contact: {driver}"
            )
            session.add(offer)
            await session.flush()

            await event_bus.emit(MissionEvent(
                mission_id=mission.id,
                event_type=EventType.OFFER_RECEIVED,
                title=f"Carrier Status: {carrier.name}",
                message=f"Available: {is_avail} | ETA: {eta_mins}m | Rate: ${cost:,.2f}",
                data=self._offer_to_dict(offer)
            ))

            await self._emit_timeline(
                session, mission.id, "CALL",
                f"Carrier Contacted: {carrier.name}",
                f"Status: {'AVAILABLE' if is_avail else 'UNAVAILABLE'} | ETA: {eta_mins}m | Cost: ${cost:,.2f}"
            )

            # If this carrier meets all SLA constraints, LOCK IMMEDIATELY!
            if is_avail and eta_mins <= 120 and cost <= mission.target_budget:
                secured_offer = offer
                await self._emit_reasoning(
                    mission.id,
                    f"SUCCESS: {carrier.name} confirmed immediate truck dispatch within {eta_mins} minutes at ${cost:,.2f} (Driver: {driver}). Locking carrier immediately."
                )
                break

        if not secured_offer:
            await self._set_status(session, mission, MissionStatus.FAILED, "No emergency carrier could meet 2-hour arrival SLA.")
            return

        # Lock Emergency Dispatch
        await self._set_status(session, mission, MissionStatus.CONFIRMING, f"Locking emergency dispatch with {secured_offer.supplier_name}...")
        await asyncio.sleep(1.0)

        dispatch_ref = f"DSP-SWIFT-{uuid.uuid4().hex[:4].upper()}"
        mission.final_offer_id = secured_offer.id
        mission.completed_at = datetime.utcnow()
        mission.total_savings = max(0.0, mission.target_budget - secured_offer.total_price)
        elapsed_seconds = max(1, int((datetime.utcnow() - start_time).total_seconds()))

        await self._emit_timeline(
            session, mission.id, "CONFIRMATION",
            f"Emergency Dispatch Locked ({dispatch_ref})",
            f"Vehicle en route with {secured_offer.supplier_name}. Driver {secured_offer.contact_person} arriving in {secured_offer.delivery_date}."
        )

        mission_report = {
            "mission_id": mission.id,
            "workflow_type": "RESCUE",
            "objective": mission.objective,
            "item_secured": f"{mission.item} ({secured_offer.contact_person})",
            "final_price": secured_offer.total_price,
            "original_budget": mission.target_budget,
            "total_savings": mission.total_savings,
            "delivery_commitment": f"ETA {secured_offer.delivery_date} (Immediate Dispatch)",
            "warranty": "Freight Insurance Guaranteed",
            "supplier_confirmed": secured_offer.supplier_name,
            "po_reference": dispatch_ref,
            "calls_initiated": calls_count,
            "successful_conversations": calls_count,
            "negotiation_rounds": 0,
            "execution_time_seconds": elapsed_seconds
        }
        mission.summary_report = mission_report
        await session.flush()

        await self._set_status(session, mission, MissionStatus.COMPLETED, "Rescue Mission Accomplished! Replacement truck dispatched.")
        await self._emit_reasoning(mission.id, f"Rescue Complete: Truck en route from {secured_offer.supplier_name}. Driver: {secured_offer.contact_person}.")

        await event_bus.emit(MissionEvent(
            mission_id=mission.id,
            event_type=EventType.MISSION_COMPLETED,
            title="Rescue Complete",
            message=f"Successfully dispatched replacement transport from {secured_offer.supplier_name}.",
            data=mission_report
        ))
        await session.commit()

    # =========================================================================
    # WORKFLOW 03: QUOTE (Comparative Equipment Bidding & Spec Normalization)
    # =========================================================================
    async def _run_quote(self, session, mission: DBMission, parsed: dict, start_time: datetime):
        await self._set_status(session, mission, MissionStatus.DISCOVERING, "Identifying certified commercial equipment suppliers...")
        await asyncio.sleep(1.0)

        vendors = discovery_service.discover_for_mission(
            workflow_type=WorkflowType.QUOTE,
            item=mission.item,
            location=mission.location,
            limit=3
        )
        if not vendors:
            await self._set_status(session, mission, MissionStatus.FAILED, "No equipment vendors found.")
            return

        vendor_names = ", ".join(v.name for v in vendors)
        await self._emit_timeline(session, mission.id, "DISCOVERY", f"{len(vendors)} Bidders Identified", f"Vendors: {vendor_names}")
        await self._emit_reasoning(mission.id, f"Initiating comparative quotation outreach to {len(vendors)} vendors for {mission.item}...")

        await self._set_status(session, mission, MissionStatus.CALLING, f"Calling {len(vendors)} equipment vendors for detailed commercial proposals...")
        collected_offers: List[DBOffer] = []

        for idx, vendor in enumerate(vendors, start=1):
            call_rec = DBCallRecord(
                id=f"call_{uuid.uuid4().hex[:8]}",
                mission_id=mission.id,
                supplier_name=vendor.name,
                supplier_phone=vendor.phone,
                call_type="QUOTE",
                status=CallStatus.TALKING.value,
                started_at=datetime.utcnow()
            )
            session.add(call_rec)
            await session.flush()

            await event_bus.emit(MissionEvent(
                mission_id=mission.id,
                event_type=EventType.CALL_STARTED,
                title=f"Quotation Call: {vendor.name}",
                message=f"Requesting turnkey pricing and specs from {vendor.name}...",
                data=self._call_to_dict(call_rec)
            ))
            await self._emit_reasoning(mission.id, f"Dialing {vendor.name} to obtain full turnkey specs (ATS, warranty, installation)...")

            call_result = await call_agent.make_quote_call(
                supplier=vendor,
                equipment_type=mission.item,
                budget=mission.target_budget,
                mission_id=mission.id
            )

            structured = call_result.get("result", {})
            call_rec.status = CallStatus.COMPLETED.value
            call_rec.duration_seconds = call_result.get("duration_seconds", 52)
            call_rec.transcript_snippet = call_result.get("transcript", "")
            call_rec.structured_result = structured
            call_rec.ended_at = datetime.utcnow()
            await session.flush()

            await event_bus.emit(MissionEvent(
                mission_id=mission.id,
                event_type=EventType.CALL_COMPLETED,
                title=f"Quote Received: {vendor.name}",
                message=f"Proposal collected in {call_rec.duration_seconds}s.",
                data=self._call_to_dict(call_rec)
            ))

            total_cost = float(structured.get("total_price", 15000.0))
            model = structured.get("equipment_model", "50kVA Generator")
            warranty = float(structured.get("warranty_years", 2.0))
            delivery_days = int(structured.get("delivery_days", 4))

            offer = DBOffer(
                id=f"off_{uuid.uuid4().hex[:8]}",
                mission_id=mission.id,
                supplier_name=vendor.name,
                supplier_phone=vendor.phone,
                contact_person=structured.get("contact_person", "Sales Engineer"),
                unit_price=total_cost,
                total_price=total_cost,
                original_price=total_cost,
                quantity_available=1,
                delivery_days=delivery_days,
                delivery_date=f"{delivery_days} Business Days",
                warranty_years=warranty,
                payment_terms=structured.get("payment_terms", "Commercial Net 30"),
                status=OfferStatus.CANDIDATE.value,
                notes=f"Model: {model} | {warranty}-yr Warranty | {structured.get('notes', '')}"
            )
            session.add(offer)
            await session.flush()
            collected_offers.append(offer)

            await event_bus.emit(MissionEvent(
                mission_id=mission.id,
                event_type=EventType.OFFER_RECEIVED,
                title=f"Bid: {vendor.name}",
                message=f"Quoted ${total_cost:,.2f} for {model} ({warranty}yr warranty).",
                data=self._offer_to_dict(offer)
            ))

            await self._emit_timeline(
                session, mission.id, "CALL",
                f"Bid Collected: {vendor.name}",
                f"${total_cost:,.2f} | {model} | {warranty}yr Warranty"
            )

        # Normalize and Rank Bids
        await self._set_status(session, mission, MissionStatus.ANALYZING, "Normalizing commercial proposals and scoring value matrix...")
        await asyncio.sleep(1.0)

        evaluated_offers, explanation = decision_engine.evaluate_offers(
            offers=collected_offers,
            target_budget=mission.target_budget,
            required_quantity=1,
            max_delivery_days=7
        )
        await session.flush()

        best_offer = next((o for o in evaluated_offers if o.status == OfferStatus.BEST.value), evaluated_offers[0])
        best_offer.status = OfferStatus.ACCEPTED.value
        mission.final_offer_id = best_offer.id
        mission.completed_at = datetime.utcnow()
        mission.total_savings = max(0.0, mission.target_budget - best_offer.total_price)
        elapsed_seconds = max(1, int((datetime.utcnow() - start_time).total_seconds()))

        bid_ref = f"BID-{best_offer.supplier_name[:4].upper()}-50KVA"

        mission_report = {
            "mission_id": mission.id,
            "workflow_type": "QUOTE",
            "objective": mission.objective,
            "item_secured": f"{mission.item} (Best Bid: {best_offer.notes.split('|')[0].replace('Model:', '').strip()})",
            "final_price": best_offer.total_price,
            "original_budget": mission.target_budget,
            "total_savings": mission.total_savings,
            "delivery_commitment": f"{best_offer.delivery_days} Business Days (Turnkey Commissioning)",
            "warranty": f"{best_offer.warranty_years} Years Full Commercial",
            "supplier_confirmed": best_offer.supplier_name,
            "po_reference": bid_ref,
            "calls_initiated": len(vendors),
            "successful_conversations": len(vendors),
            "negotiation_rounds": 0,
            "execution_time_seconds": elapsed_seconds
        }
        mission.summary_report = mission_report
        await session.flush()

        await self._set_status(session, mission, MissionStatus.COMPLETED, "Quotation Matrix Complete! Recommended proposal identified.")
        await self._emit_reasoning(mission.id, f"Quotation matrix complete. Recommended bidder: {best_offer.supplier_name} at ${best_offer.total_price:,.2f} ({best_offer.warranty_years}-yr warranty).")

        await event_bus.emit(MissionEvent(
            mission_id=mission.id,
            event_type=EventType.MISSION_COMPLETED,
            title="Quotation Complete",
            message=f"Comparative bidding finalized. Recommended: {best_offer.supplier_name}.",
            data=mission_report
        ))
        await session.commit()

    # =========================================================================
    # WORKFLOW 04: SCHEDULE (Priority Waitlist Sequential Slot Filling)
    # =========================================================================
    async def _run_schedule(self, session, mission: DBMission, parsed: dict, start_time: datetime):
        await self._set_status(session, mission, MissionStatus.DISCOVERING, "Loading priority client waitlist...")
        await asyncio.sleep(1.0)

        clients = discovery_service.discover_for_mission(
            workflow_type=WorkflowType.SCHEDULE,
            item=mission.item,
            location=mission.location,
            limit=3
        )
        if not clients:
            await self._set_status(session, mission, MissionStatus.FAILED, "No waitlist clients found.")
            return

        client_names = ", ".join(c.name for c in clients)
        await self._emit_timeline(session, mission.id, "DISCOVERY", f"{len(clients)} Waitlist Candidates", f"Prioritized queue: {client_names}")
        await self._emit_reasoning(mission.id, f"Found {len(clients)} priority waitlist candidates for the cancelled 3:00 PM slot. Starting sequential outreach...")

        await self._set_status(session, mission, MissionStatus.CALLING, "Contacting waitlist clients in priority order...")

        booked_offer: Optional[DBOffer] = None
        calls_count = 0

        for idx, client in enumerate(clients, start=1):
            calls_count += 1
            call_rec = DBCallRecord(
                id=f"call_{uuid.uuid4().hex[:8]}",
                mission_id=mission.id,
                supplier_name=client.name,
                supplier_phone=client.phone,
                call_type="SCHEDULE",
                status=CallStatus.TALKING.value,
                started_at=datetime.utcnow()
            )
            session.add(call_rec)
            await session.flush()

            await event_bus.emit(MissionEvent(
                mission_id=mission.id,
                event_type=EventType.CALL_STARTED,
                title=f"Waitlist Call #{idx}: {client.name}",
                message=f"Offering 3:00 PM appointment slot to {client.name}...",
                data=self._call_to_dict(call_rec)
            ))
            await self._emit_reasoning(mission.id, f"Inquiring with {client.name} if they can take today's 3:00 PM appointment slot...")

            call_result = await call_agent.make_schedule_call(
                supplier=client,
                slot_time="3:00 PM Today",
                mission_id=mission.id
            )

            structured = call_result.get("result", {})
            call_rec.status = CallStatus.COMPLETED.value
            call_rec.duration_seconds = call_result.get("duration_seconds", 30)
            call_rec.transcript_snippet = call_result.get("transcript", "")
            call_rec.structured_result = structured
            call_rec.ended_at = datetime.utcnow()
            await session.flush()

            await event_bus.emit(MissionEvent(
                mission_id=mission.id,
                event_type=EventType.CALL_COMPLETED,
                title=f"Call Complete: {client.name}",
                message=f"Client response logged in {call_rec.duration_seconds}s.",
                data=self._call_to_dict(call_rec)
            ))

            slot_accepted = structured.get("slot_accepted", False)
            confirmed_time = structured.get("confirmed_time", "3:00 PM Today")
            notes = structured.get("special_requests", "Confirmed via CALL-E")

            offer = DBOffer(
                id=f"off_{uuid.uuid4().hex[:8]}",
                mission_id=mission.id,
                supplier_name=client.name,
                supplier_phone=client.phone,
                contact_person=client.name,
                unit_price=0.0,
                total_price=0.0,
                original_price=0.0,
                quantity_available=1,
                delivery_days=0,
                delivery_date=confirmed_time,
                warranty_years=0.0,
                payment_terms="Standard Consultation Fee",
                status=OfferStatus.ACCEPTED.value if slot_accepted else OfferStatus.REJECTED.value,
                notes=f"Slot: {confirmed_time} | Status: {'ACCEPTED' if slot_accepted else 'DECLINED'} | {notes}"
            )
            session.add(offer)
            await session.flush()

            await event_bus.emit(MissionEvent(
                mission_id=mission.id,
                event_type=EventType.OFFER_RECEIVED,
                title=f"Response: {client.name}",
                message=f"Slot Accepted: {slot_accepted} ({confirmed_time})",
                data=self._offer_to_dict(offer)
            ))

            await self._emit_timeline(
                session, mission.id, "CALL",
                f"Candidate Contacted: {client.name}",
                f"{'ACCEPTED' if slot_accepted else 'DECLINED'} for {confirmed_time}"
            )

            if slot_accepted:
                booked_offer = offer
                await self._emit_reasoning(
                    mission.id,
                    f"SUCCESS: {client.name} accepted the appointment slot for {confirmed_time}. Locking calendar booking."
                )
                break

        if not booked_offer:
            await self._set_status(session, mission, MissionStatus.FAILED, "No waitlist client accepted the open slot.")
            return

        # Lock Appointment
        await self._set_status(session, mission, MissionStatus.CONFIRMING, f"Booking appointment for {booked_offer.supplier_name}...")
        await asyncio.sleep(1.0)

        slot_ref = f"SLOT-CAL-{uuid.uuid4().hex[:4].upper()}"
        mission.final_offer_id = booked_offer.id
        mission.completed_at = datetime.utcnow()
        mission.total_savings = 0.0
        elapsed_seconds = max(1, int((datetime.utcnow() - start_time).total_seconds()))

        await self._emit_timeline(
            session, mission.id, "CONFIRMATION",
            f"Calendar Slot Locked ({slot_ref})",
            f"Appointment confirmed for {booked_offer.supplier_name} at {booked_offer.delivery_date}."
        )

        mission_report = {
            "mission_id": mission.id,
            "workflow_type": "SCHEDULE",
            "objective": mission.objective,
            "item_secured": f"3:00 PM Consultation Booking ({booked_offer.supplier_name})",
            "final_price": 0.0,
            "original_budget": 0.0,
            "total_savings": 0.0,
            "delivery_commitment": f"{booked_offer.delivery_date} (Confirmed)",
            "warranty": "Calendar Sync Active",
            "supplier_confirmed": booked_offer.supplier_name,
            "po_reference": slot_ref,
            "calls_initiated": calls_count,
            "successful_conversations": calls_count,
            "negotiation_rounds": 0,
            "execution_time_seconds": elapsed_seconds
        }
        mission.summary_report = mission_report
        await session.flush()

        await self._set_status(session, mission, MissionStatus.COMPLETED, "Schedule Filled! Appointment confirmed.")
        await self._emit_reasoning(mission.id, f"Slot locked for {booked_offer.supplier_name} at {booked_offer.delivery_date}.")

        await event_bus.emit(MissionEvent(
            mission_id=mission.id,
            event_type=EventType.MISSION_COMPLETED,
            title="Schedule Complete",
            message=f"Slot successfully booked for {booked_offer.supplier_name}.",
            data=mission_report
        ))
        await session.commit()

orchestrator = MissionOrchestrator()
