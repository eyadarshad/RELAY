import os
import asyncio
import logging
import httpx
from typing import Dict, Any, Optional
from backend.config import settings

logger = logging.getLogger(__name__)

class CalleAdapter:
    """
    Adapter for CALL-E API / SDK.
    Supports:
    1. Real outbound calls via official CALL-E Python SDK (calle-ai / CalleClient)
    2. Fallback to direct HTTP Calls API (v1) with strict result_schema validation
    3. High-fidelity conversational simulation engine for offline testing & rapid demo fallback
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.CALLE_API_KEY
        self.api_url = settings.CALLE_API_URL.rstrip("/")
        self._sdk_client: Optional[Any] = None

        if self.api_key and not settings.FORCE_SIMULATION:
            try:
                from calle import CalleClient
                self._sdk_client = CalleClient(api_key=self.api_key)
                logger.info("CALL-E Official SDK Client (calle-ai) successfully initialized with API key.")
            except ImportError:
                logger.info("calle-ai Python SDK package not detected; will use direct REST API.")
            except Exception as e:
                logger.warning(f"Could not initialize CalleClient SDK: {e}. Will fallback to REST API.")

    @property
    def is_live_enabled(self) -> bool:
        return bool(self.api_key) and not settings.FORCE_SIMULATION

    async def create_and_wait_call(
        self,
        task: str,
        result_schema: Dict[str, Any],
        recipient_phone: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        timeout_seconds: int = 120
    ) -> Dict[str, Any]:
        """
        Creates a call task and waits for terminal outcome.
        If live API key is configured, uses CALL-E SDK/API.
        Otherwise, executes dynamic AI conversational simulation based on supplier persona.
        """
        if self.is_live_enabled:
            return await self._execute_real_calle_call(
                task=task,
                result_schema=result_schema,
                recipient_phone=recipient_phone,
                metadata=metadata,
                idempotency_key=idempotency_key,
                timeout_seconds=timeout_seconds
            )
        else:
            return await self._execute_simulated_call(
                task=task,
                result_schema=result_schema,
                recipient_phone=recipient_phone,
                metadata=metadata
            )

    async def _execute_real_calle_call(
        self,
        task: str,
        result_schema: Dict[str, Any],
        recipient_phone: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        timeout_seconds: int = 120
    ) -> Dict[str, Any]:
        """
        Executes real phone call using official CALL-E Python SDK (or HTTP fallback).
        """
        logger.info(f"Initiating REAL CALL-E call for task: {task[:60]}...")

        # 1. Attempt using official SDK if initialized
        if self._sdk_client:
            try:
                def _run_sdk():
                    # Build call params for official SDK
                    params: Dict[str, Any] = {
                        "task": task,
                        "result_schema": result_schema,
                    }
                    if recipient_phone:
                        params["recipients"] = [{"phones": [recipient_phone]}]
                    if metadata:
                        params["metadata"] = metadata
                    if idempotency_key:
                        params["idempotency_key"] = idempotency_key

                    # create_and_wait with timeout
                    try:
                        return self._sdk_client.calls.create_and_wait(
                            timeout_seconds=timeout_seconds,
                            interval_seconds=2,
                            **params
                        )
                    except AttributeError:
                        # Fallback for SDK versions with separate create + wait_for_result
                        created = self._sdk_client.calls.create(**params)
                        call_id = created.get("id") if isinstance(created, dict) else getattr(created, "id", None)
                        return self._sdk_client.calls.wait_for_result(
                            call_id,
                            timeout_seconds=timeout_seconds,
                            interval_seconds=2
                        )

                # Wrap synchronous SDK call in thread
                sdk_result = await asyncio.to_thread(_run_sdk)
                logger.info("CALL-E SDK call returned successfully.")

                # Extract data safely from SDK response dict or object
                call_id = sdk_result.get("id") if isinstance(sdk_result, dict) else getattr(sdk_result, "id", f"calle_{os.urandom(4).hex()}")
                status = sdk_result.get("status") if isinstance(sdk_result, dict) else getattr(sdk_result, "status", "completed")
                structured = sdk_result.get("structured_result") if isinstance(sdk_result, dict) else getattr(sdk_result, "structured_result", getattr(sdk_result, "result", {}))
                duration = sdk_result.get("duration_seconds") if isinstance(sdk_result, dict) else getattr(sdk_result, "duration_seconds", 45)
                transcript = sdk_result.get("transcript") if isinstance(sdk_result, dict) else getattr(sdk_result, "transcript", "")
                evidence = sdk_result.get("evidence") if isinstance(sdk_result, dict) else getattr(sdk_result, "evidence", [])

                if not transcript and evidence:
                    transcript = "\n".join(str(e) for e in evidence)

                return {
                    "id": call_id,
                    "status": status,
                    "result": structured or {},
                    "duration_seconds": duration,
                    "transcript": transcript or "Real CALL-E call executed and structured output extracted.",
                    "is_real_call": True
                }
            except Exception as e:
                logger.warning(f"CALL-E SDK call failed: {e}. Attempting direct HTTP fallback...")

        # 2. Direct HTTP REST fallback
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        payload: Dict[str, Any] = {
            "task": task,
            "result_schema": result_schema,
            "metadata": metadata or {}
        }
        if recipient_phone:
            payload["recipients"] = [{"phones": [recipient_phone]}]

        async with httpx.AsyncClient(timeout=timeout_seconds) as http_client:
            # 1. Create call task
            response = await http_client.post(
                f"{self.api_url}/calls",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            call_data = response.json()
            call_id = call_data.get("id")

            # 2. Poll until terminal state
            start_time = asyncio.get_event_loop().time()
            while asyncio.get_event_loop().time() - start_time < timeout_seconds:
                await asyncio.sleep(2)
                poll_resp = await http_client.get(
                    f"{self.api_url}/calls/{call_id}",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                if poll_resp.status_code == 200:
                    current_call = poll_resp.json()
                    status = current_call.get("status")
                    if status in ["completed", "failed", "cancelled", "unsupported_region"]:
                        return {
                            "id": call_id,
                            "status": status,
                            "result": current_call.get("structured_result") or current_call.get("result", {}),
                            "duration_seconds": current_call.get("duration_seconds", 30),
                            "transcript": current_call.get("transcript", "CALL-E call completed."),
                            "is_real_call": True
                        }

            # Timeout
            return {
                "id": call_id,
                "status": "failed",
                "result": {},
                "error": "Call timed out waiting for completion",
                "is_real_call": True
            }

    async def _execute_simulated_call(
        self,
        task: str,
        result_schema: Dict[str, Any],
        recipient_phone: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Simulates realistic human conversation based on the target supplier persona.
        Adds realistic 3-5 second delay to demonstrate real-time WebSocket updates.
        """
        meta = metadata or {}
        supplier_name = meta.get("supplier_name", "Supplier")
        call_type = meta.get("call_type", "INQUIRY")
        
        logger.info(f"Simulating realistic call with {supplier_name} ({call_type})...")
        await asyncio.sleep(3.5)  # Simulate realistic telephony cadence

        # --- WORKFLOW 1: PROCURE PERSONAS ---
        if "XYZ" in supplier_name:
            if call_type == "NEGOTIATION":
                return {
                    "id": f"sim_calle_{os.urandom(4).hex()}",
                    "status": "completed",
                    "result": {
                        "negotiation_success": True,
                        "revised_total_price": 13700.0,
                        "revised_unit_price": 27.40,
                        "discount_amount": 1000.0,
                        "extra_concessions": "Free priority freight & 2-year extended commercial warranty included",
                        "conditions_for_discount": "Full 500 unit commitment confirmed today"
                    },
                    "duration_seconds": 64,
                    "transcript": "Agent: 'We have another comparable offer from OfficePro at $14,100. Is there any flexibility if we confirm all 500 units today?'\nAli (XYZ): 'If you can confirm today, I can authorize our maximum commercial volume discount at $27.40/chair, bringing total to $13,700 with full 2-year warranty.'\nAgent: 'Understood, that is very competitive. We will submit for purchase approval.'",
                    "is_real_call": False
                }
            elif call_type == "CONFIRMATION":
                return {
                    "id": f"sim_calle_{os.urandom(4).hex()}",
                    "status": "completed",
                    "result": {
                        "order_confirmed": True,
                        "order_reference_number": "PO-XYZ-2026-0941",
                        "final_agreed_amount": 13700.0,
                        "delivery_commitment_date": "Thursday, September 4",
                        "support_contact": "+1 (415) 555-0191"
                    },
                    "duration_seconds": 45,
                    "transcript": "Agent: 'Calling to confirm Purchase Order for 500 ergonomic chairs at $13,700 total.'\nAli (XYZ): 'Confirmed! Order reference PO-XYZ-2026-0941. Shipment is scheduled for dispatch tomorrow, arriving Thursday, September 4.'",
                    "is_real_call": False
                }
            else: # Standard initial inquiry
                return {
                    "id": f"sim_calle_{os.urandom(4).hex()}",
                    "status": "completed",
                    "result": {
                        "availability": True,
                        "quantity_available": 750,
                        "unit_price": 29.40,
                        "total_price": 14700.0,
                        "delivery_days": 4,
                        "warranty_years": 2.0,
                        "payment_terms": "50% upfront, 50% upon delivery",
                        "contact_person": "Ali (Commercial Sales Lead)",
                        "negotiable": True,
                        "notes": "Has 750 units in stock. High grade mesh ergonomic model. Representative stated price is flexible for instant corporate close."
                    },
                    "duration_seconds": 58,
                    "transcript": "Agent: 'Hi Ali, we need 500 ergonomic office chairs delivered to Lahore by Friday. What is your pricing and stock?'\nAli: 'We have 750 units in our central warehouse. Standard commercial rate is $29.40/unit ($14,700 total), with 4-day delivery and 2-year warranty.'",
                    "is_real_call": False
                }
        
        elif "ABC" in supplier_name:
            return {
                "id": f"sim_calle_{os.urandom(4).hex()}",
                "status": "completed",
                "result": {
                    "availability": True,
                    "quantity_available": 900,
                    "unit_price": 30.40,
                    "total_price": 15200.0,
                    "delivery_days": 3,
                    "warranty_years": 1.0,
                    "payment_terms": "Net 15",
                    "contact_person": "Bilal",
                    "negotiable": False,
                    "notes": "Exceeds $15,000 maximum budget. Representative stated firm pricing with no volume discount."
                },
                "duration_seconds": 42,
                "transcript": "Agent: 'Inquiring about 500 chairs delivered this week.'\nBilal (ABC): 'We can do $30.40 per chair, total $15,200. Pricing is fixed for this quarter. Delivery in 3 days.'",
                "is_real_call": False
            }

        elif "OfficePro" in supplier_name:
            return {
                "id": f"sim_calle_{os.urandom(4).hex()}",
                "status": "completed",
                "result": {
                    "availability": True,
                    "quantity_available": 600,
                    "unit_price": 28.20,
                    "total_price": 14100.0,
                    "delivery_days": 5,
                    "warranty_years": 2.0,
                    "payment_terms": "100% on delivery",
                    "contact_person": "Hamza",
                    "negotiable": False,
                    "notes": "Good price at $14,100, but delivery timeline is 5-6 days which cuts very close to Friday deadline."
                },
                "duration_seconds": 51,
                "transcript": "Hamza (OfficePro): 'We have 600 units available at $28.20 each ($14,100 total). Delivery takes 5 full business days.'",
                "is_real_call": False
            }

        elif "MegaOffice" in supplier_name:
            return {
                "id": f"sim_calle_{os.urandom(4).hex()}",
                "status": "completed",
                "result": {
                    "availability": False,
                    "quantity_available": 250,
                    "unit_price": 25.00,
                    "total_price": 12500.0,
                    "delivery_days": 2,
                    "warranty_years": 1.0,
                    "payment_terms": "Advance payment",
                    "contact_person": "Tariq",
                    "negotiable": False,
                    "notes": "Insufficient stock. Only 250 units in warehouse; remaining 250 on 3-week backorder."
                },
                "duration_seconds": 38,
                "transcript": "Tariq (MegaOffice): 'We only have 250 units in stock right now. The rest won't arrive for 3 weeks.'",
                "is_real_call": False
            }

        # --- WORKFLOW 2: RESCUE PERSONAS ---
        elif "Swift" in supplier_name or "Express" in supplier_name:
            return {
                "id": f"sim_calle_{os.urandom(4).hex()}",
                "status": "completed",
                "result": {
                    "service_available": True,
                    "eta_minutes": 45,
                    "total_cost": 480.0,
                    "driver_contact": "Captain Naveed (+1-415-555-0201)",
                    "notes": "26ft box truck standing by in central district. Immediate dispatch."
                },
                "duration_seconds": 35,
                "transcript": "Agent: 'We need an emergency 26ft box truck dispatched immediately to our depot. Are you available within 2 hours?'\nDispatcher (Swift): 'Yes! We have a 26ft truck on stand-by near the downtown interchange. Captain Naveed can arrive at your dock in 45 minutes for a $480 flat dispatch rate.'\nAgent: 'Excellent, locking in the dispatch.'",
                "is_real_call": False
            }

        elif "Titan" in supplier_name or "Haulers" in supplier_name:
            return {
                "id": f"sim_calle_{os.urandom(4).hex()}",
                "status": "completed",
                "result": {
                    "service_available": True,
                    "eta_minutes": 90,
                    "total_cost": 620.0,
                    "driver_contact": "Dispatch Hotline (+1-415-555-0202)",
                    "notes": "Available in 90 minutes. Freight rate $620."
                },
                "duration_seconds": 32,
                "transcript": "Dispatcher (Titan): 'We have a unit returning from a run. Could reach you in approximately 90 minutes for $620.'",
                "is_real_call": False
            }

        elif "Apex Express" in supplier_name or "Cargo" in supplier_name:
            return {
                "id": f"sim_calle_{os.urandom(4).hex()}",
                "status": "completed",
                "result": {
                    "service_available": False,
                    "eta_minutes": 240,
                    "total_cost": 0.0,
                    "driver_contact": "N/A",
                    "notes": "All fleet vehicles currently dispatched on scheduled routes."
                },
                "duration_seconds": 25,
                "transcript": "Dispatcher (Apex Cargo): 'Sorry, all our box trucks are currently committed on airport runs until 7 PM tonight.'",
                "is_real_call": False
            }

        # --- WORKFLOW 3: QUOTE PERSONAS ---
        elif "Voltech" in supplier_name or "Voltech Power" in supplier_name:
            return {
                "id": f"sim_calle_{os.urandom(4).hex()}",
                "status": "completed",
                "result": {
                    "availability": True,
                    "equipment_model": "Cummins 50kVA Diesel Generator (Soundproof Silent Canopy)",
                    "total_price": 14200.0,
                    "unit_price": 14200.0,
                    "quantity_available": 5,
                    "delivery_days": 4,
                    "warranty_years": 3.0,
                    "includes_installation": True,
                    "payment_terms": "30% advance, 70% post-commissioning",
                    "contact_person": "Engr. Salman (Sales Engineering)",
                    "notes": "Includes automatic transfer switch (ATS), load testing, and full 3-year commercial warranty."
                },
                "duration_seconds": 58,
                "transcript": "Agent: 'Inquiring about commercial 50kVA generator pricing including warranty and installation.'\nEngr. Salman (Voltech): 'We can provide the Cummins 50kVA soundproof generator for $14,200 total, including on-site ATS installation and full 3-year parts & labor warranty. Delivery in 4 business days.'",
                "is_real_call": False
            }

        elif "Dynamo" in supplier_name or "Dynamo Industrial" in supplier_name:
            return {
                "id": f"sim_calle_{os.urandom(4).hex()}",
                "status": "completed",
                "result": {
                    "availability": True,
                    "equipment_model": "Perkins 60kVA Industrial Power Unit",
                    "total_price": 15800.0,
                    "unit_price": 15800.0,
                    "quantity_available": 8,
                    "delivery_days": 3,
                    "warranty_years": 2.0,
                    "includes_installation": True,
                    "payment_terms": "50% deposit, 50% net 30",
                    "contact_person": "Rashid Khan",
                    "notes": "Perkins 60kVA generator. 2-year warranty with 3-day rapid delivery."
                },
                "duration_seconds": 48,
                "transcript": "Rashid (Dynamo): 'Our Perkins 60kVA unit is $15,800 turnkey. Includes 2 years warranty and 3-day commissioning.'",
                "is_real_call": False
            }

        elif "Atlas" in supplier_name or "Atlas Energy" in supplier_name:
            return {
                "id": f"sim_calle_{os.urandom(4).hex()}",
                "status": "completed",
                "result": {
                    "availability": True,
                    "equipment_model": "Caterpillar CAT 50kVA Heavy Duty",
                    "total_price": 18500.0,
                    "unit_price": 18500.0,
                    "quantity_available": 12,
                    "delivery_days": 2,
                    "warranty_years": 5.0,
                    "includes_installation": True,
                    "payment_terms": "100% Letter of Credit / Corporate PO",
                    "contact_person": "Zubair Shah",
                    "notes": "CAT tier 1 generator with 5-year warranty. Premium commercial grade."
                },
                "duration_seconds": 52,
                "transcript": "Zubair (Atlas Energy): 'We quote the Caterpillar 50kVA at $18,500 with 5-year extended warranty.'",
                "is_real_call": False
            }

        # --- WORKFLOW 4: SCHEDULE PERSONAS ---
        elif "Sarah" in supplier_name or "Dr. Sarah" in supplier_name:
            return {
                "id": f"sim_calle_{os.urandom(4).hex()}",
                "status": "completed",
                "result": {
                    "slot_accepted": True,
                    "patient_or_client_name": "Dr. Sarah Khan",
                    "confirmed_time": "Today at 3:00 PM",
                    "special_requests": "Requesting brief intake file review 10 minutes prior"
                },
                "duration_seconds": 31,
                "transcript": "Agent: 'Hello Dr. Sarah, a 3:00 PM consultation slot has just opened up today due to a cancellation. As top priority on our waitlist, would you like to take this appointment?'\nDr. Sarah: 'Yes, absolutely! I have been waiting for a 3 PM opening all week. Please confirm my booking immediately.'\nAgent: 'Confirmed. You are booked for today at 3:00 PM.'",
                "is_real_call": False
            }

        elif "Tariq" in supplier_name:
            return {
                "id": f"sim_calle_{os.urandom(4).hex()}",
                "status": "completed",
                "result": {
                    "slot_accepted": False,
                    "patient_or_client_name": "Tariq Mansoor",
                    "confirmed_time": "None",
                    "special_requests": "Keep on waitlist for tomorrow morning"
                },
                "duration_seconds": 26,
                "transcript": "Tariq: 'Thank you for calling, but I have a conflicting board meeting at 3 PM today. Please keep me on the waitlist for tomorrow.'",
                "is_real_call": False
            }

        # Generic fallback
        return {
            "id": f"sim_calle_{os.urandom(4).hex()}",
            "status": "completed",
            "result": {
                "availability": True,
                "quantity_available": 500,
                "unit_price": 28.50,
                "total_price": 14250.0,
                "delivery_days": 4,
                "warranty_years": 1.5,
                "payment_terms": "Standard",
                "contact_person": "Sales Desk",
                "negotiable": True,
                "notes": "Standard commercial proposal meeting baseline parameters."
            },
            "duration_seconds": 30,
            "transcript": "Representative confirmed product availability and standard pricing terms.",
            "is_real_call": False
        }

calle_adapter = CalleAdapter()
