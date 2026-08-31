import logging
from typing import Dict, Any, Optional
from backend.models import Supplier, DBCallRecord, CallStatus
from backend.calle.adapter import calle_adapter
from backend.calle.schemas import (
    SUPPLIER_INQUIRY_SCHEMA,
    NEGOTIATION_SCHEMA,
    CONFIRMATION_SCHEMA,
    RESCUE_SCHEMA,
    COMMERCIAL_QUOTE_SCHEMA,
    SCHEDULE_SCHEMA
)

logger = logging.getLogger(__name__)

class CallAgent:
    """
    Coordinates phone call execution using CALL-E for inquiry, negotiation, confirmation, rescue, quotes, and waitlist scheduling.
    """

    async def make_inquiry_call(
        self,
        supplier: Supplier,
        item: str,
        quantity: int,
        budget: float,
        deadline: str,
        mission_id: str
    ) -> Dict[str, Any]:
        task = f"""
Call {supplier.phone} at {supplier.name} located in {supplier.location}.
You are calling as an authorized corporate operations manager.

Primary Mission: We urgently need {quantity} {item} delivered before {deadline}.
Our target budget ceiling is ${budget:,.2f}.

Conversation Objectives:
1. Speak with commercial sales or warehouse dispatch.
2. Confirm immediate stock availability for all {quantity} units.
3. If they cannot fulfill {quantity} units, inquire how many can be delivered before {deadline}.
4. Ask for their best wholesale unit price and total price.
5. Inquire about delivery timeframe in business days.
6. Verify warranty period (years) and payment terms.
7. Ask if pricing is negotiable for immediate order placement today.

Speak naturally, concisely, and professionally. Adapt dynamically to the recipient's responses.
"""
        result = await calle_adapter.create_and_wait_call(
            task=task,
            result_schema=SUPPLIER_INQUIRY_SCHEMA,
            recipient_phone=supplier.phone,
            metadata={
                "mission_id": mission_id,
                "supplier_name": supplier.name,
                "call_type": "INQUIRY",
                "supplier_data": supplier.dict()
            }
        )
        return result

    async def make_negotiation_call(
        self,
        supplier: Supplier,
        current_offer_price: float,
        target_price: float,
        competing_offer_price: float,
        quantity: int,
        item: str,
        mission_id: str
    ) -> Dict[str, Any]:
        task = f"""
Call {supplier.phone} at {supplier.name}.
Ask to speak with the commercial representative (e.g. Ali / Sales Manager).

Context:
You previously received a quote of ${current_offer_price:,.2f} for {quantity} {item}.
We have a competing supplier offering ${competing_offer_price:,.2f}.

Negotiation Goal:
Politely negotiate the price down toward our target of ${target_price:,.2f}.
Mention that if they can discount the order to around ${target_price:,.2f} ($27.40/unit) or include extended warranty/free shipping, our management is prepared to sign and authorize the full purchase today.

Do NOT make an irreversible binding payment commitment yet, but secure their revised firm discounted quote.
"""
        result = await calle_adapter.create_and_wait_call(
            task=task,
            result_schema=NEGOTIATION_SCHEMA,
            recipient_phone=supplier.phone,
            metadata={
                "mission_id": mission_id,
                "supplier_name": supplier.name,
                "call_type": "NEGOTIATION",
                "supplier_data": supplier.dict()
            }
        )
        return result

    async def make_confirmation_call(
        self,
        supplier: Supplier,
        final_price: float,
        quantity: int,
        item: str,
        delivery_date: str,
        mission_id: str
    ) -> Dict[str, Any]:
        task = f"""
Call {supplier.phone} at {supplier.name}.
State that executive management has officially APPROVED the purchase of {quantity} {item} for the final negotiated sum of ${final_price:,.2f}.

Confirmation Goal:
1. Lock in the order under our approved budget of ${final_price:,.2f}.
2. Confirm the agreed delivery date ({delivery_date}).
3. Obtain their official Purchase Order / confirmation reference number.
4. Verify dispatch tracking contact.
"""
        result = await calle_adapter.create_and_wait_call(
            task=task,
            result_schema=CONFIRMATION_SCHEMA,
            recipient_phone=supplier.phone,
            metadata={
                "mission_id": mission_id,
                "supplier_name": supplier.name,
                "call_type": "CONFIRMATION",
                "supplier_data": supplier.dict()
            }
        )
        return result

    async def make_rescue_call(
        self,
        supplier: Supplier,
        service_needed: str,
        eta_target: str,
        mission_id: str
    ) -> Dict[str, Any]:
        task = f"""
Emergency dispatch call to {supplier.name} at {supplier.phone}.
Our primary logistics transport cancelled/broke down. We urgently require immediate {service_needed} with arrival within {eta_target}.
Inquire if an emergency truck/driver can dispatch immediately, confirm their exact ETA in minutes, and flat-rate emergency dispatch rate.
"""
        return await calle_adapter.create_and_wait_call(
            task=task,
            result_schema=RESCUE_SCHEMA,
            recipient_phone=supplier.phone,
            metadata={
                "mission_id": mission_id,
                "supplier_name": supplier.name,
                "call_type": "RESCUE",
                "supplier_data": supplier.dict()
            }
        )

    async def make_quote_call(
        self,
        supplier: Supplier,
        equipment_type: str,
        budget: float,
        mission_id: str
    ) -> Dict[str, Any]:
        task = f"""
Call commercial equipment supplier {supplier.name} at {supplier.phone}.
Request a formal commercial proposal for {equipment_type}.
Target budget is under ${budget:,.2f}.
Inquire about available equipment models, turnkey price with installation and ATS switch, delivery ETA, and warranty coverage.
"""
        return await calle_adapter.create_and_wait_call(
            task=task,
            result_schema=COMMERCIAL_QUOTE_SCHEMA,
            recipient_phone=supplier.phone,
            metadata={
                "mission_id": mission_id,
                "supplier_name": supplier.name,
                "call_type": "QUOTE",
                "supplier_data": supplier.dict()
            }
        )

    async def make_schedule_call(
        self,
        supplier: Supplier,
        slot_time: str,
        mission_id: str
    ) -> Dict[str, Any]:
        task = f"""
Call priority waitlist client {supplier.name} at {supplier.phone}.
Inform them that a cancelled slot has opened today for {slot_time}.
Ask if they wish to accept and confirm this appointment slot immediately.
"""
        return await calle_adapter.create_and_wait_call(
            task=task,
            result_schema=SCHEDULE_SCHEMA,
            recipient_phone=supplier.phone,
            metadata={
                "mission_id": mission_id,
                "supplier_name": supplier.name,
                "call_type": "SCHEDULE",
                "supplier_data": supplier.dict()
            }
        )

call_agent = CallAgent()
