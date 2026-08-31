from typing import Dict, Any

SUPPLIER_INQUIRY_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": [
        "availability",
        "quantity_available",
        "unit_price",
        "total_price",
        "delivery_days"
    ],
    "properties": {
        "availability": {
            "type": "boolean",
            "description": "Whether the supplier can provide the requested items"
        },
        "quantity_available": {
            "type": "integer",
            "description": "How many units the supplier currently has or can deliver on time"
        },
        "unit_price": {
            "type": "number",
            "description": "Quoted price per single unit in USD"
        },
        "total_price": {
            "type": "number",
            "description": "Total quoted price including standard shipping or discounts"
        },
        "delivery_days": {
            "type": "integer",
            "description": "Estimated delivery time in calendar/business days"
        },
        "warranty_years": {
            "type": "number",
            "description": "Warranty duration provided in years"
        },
        "payment_terms": {
            "type": "string",
            "description": "E.g. Net 30, 50% upfront, COD, or standard card payment"
        },
        "contact_person": {
            "type": "string",
            "description": "Name or title of the representative spoken with"
        },
        "negotiable": {
            "type": "boolean",
            "description": "Whether the representative indicated flexibility on volume pricing"
        },
        "notes": {
            "type": "string",
            "description": "Key takeaways, department info, or special conditions mentioned"
        }
    },
    "additionalProperties": False
}

NEGOTIATION_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": [
        "negotiation_success",
        "revised_total_price",
        "revised_unit_price",
        "discount_amount"
    ],
    "properties": {
        "negotiation_success": {
            "type": "boolean",
            "description": "Whether the supplier agreed to discount or improve terms"
        },
        "revised_total_price": {
            "type": "number",
            "description": "The newly agreed total price after negotiation"
        },
        "revised_unit_price": {
            "type": "number",
            "description": "The newly agreed unit price"
        },
        "discount_amount": {
            "type": "number",
            "description": "Total dollar savings achieved during this negotiation call"
        },
        "extra_concessions": {
            "type": "string",
            "description": "Any additional perks offered e.g. extended warranty, free expedited delivery"
        },
        "conditions_for_discount": {
            "type": "string",
            "description": "Conditions required by supplier e.g. confirm full order today"
        }
    },
    "additionalProperties": False
}

CONFIRMATION_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": [
        "order_confirmed",
        "order_reference_number",
        "final_agreed_amount",
        "delivery_commitment_date"
    ],
    "properties": {
        "order_confirmed": {
            "type": "boolean",
            "description": "Whether the order was successfully placed and locked in"
        },
        "order_reference_number": {
            "type": "string",
            "description": "Purchase order or booking confirmation reference from supplier"
        },
        "final_agreed_amount": {
            "type": "number",
            "description": "The final locked-in invoice total"
        },
        "delivery_commitment_date": {
            "type": "string",
            "description": "Exact confirmed arrival date"
        },
        "support_contact": {
            "type": "string",
            "description": "Direct contact or dispatch phone for tracking"
        }
    },
    "additionalProperties": False
}

RESCUE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": [
        "service_available",
        "eta_minutes",
        "total_cost"
    ],
    "properties": {
        "service_available": {
            "type": "boolean",
            "description": "Can the provider immediately dispatch a replacement unit/truck"
        },
        "eta_minutes": {
            "type": "integer",
            "description": "Time in minutes until the service provider arrives at destination"
        },
        "total_cost": {
            "type": "number",
            "description": "Emergency service cost in USD"
        },
        "driver_contact": {
            "type": "string",
            "description": "Driver name or dispatch hotline"
        },
        "notes": {
            "type": "string",
            "description": "Vehicle size, tracking link or driver details"
        }
    },
    "additionalProperties": False
}

COMMERCIAL_QUOTE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": [
        "availability",
        "equipment_model",
        "total_price",
        "delivery_days",
        "warranty_years"
    ],
    "properties": {
        "availability": {
            "type": "boolean",
            "description": "Whether the equipment model is in stock and ready for deployment"
        },
        "equipment_model": {
            "type": "string",
            "description": "Exact brand and model of generator/equipment quoted"
        },
        "total_price": {
            "type": "number",
            "description": "Total price including hardware, installation, and commissioning in USD"
        },
        "delivery_days": {
            "type": "integer",
            "description": "Days required for delivery, site delivery, and setup"
        },
        "warranty_years": {
            "type": "number",
            "description": "Warranty duration in years"
        },
        "includes_installation": {
            "type": "boolean",
            "description": "Whether on-site installation and ATS testing is included in the quote"
        },
        "payment_terms": {
            "type": "string",
            "description": "Standard commercial payment terms"
        },
        "notes": {
            "type": "string",
            "description": "Technical specifications or additional perks included"
        }
    },
    "additionalProperties": False
}

SCHEDULE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "required": [
        "slot_accepted",
        "patient_or_client_name",
        "confirmed_time"
    ],
    "properties": {
        "slot_accepted": {
            "type": "boolean",
            "description": "Did the waitlist client agree to take the newly opened slot"
        },
        "patient_or_client_name": {
            "type": "string",
            "description": "Name of the person confirmed"
        },
        "confirmed_time": {
            "type": "string",
            "description": "Appointment time confirmed"
        },
        "special_requests": {
            "type": "string",
            "description": "Any intake notes or preparation requirements"
        }
    },
    "additionalProperties": False
}
