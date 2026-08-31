from typing import Optional
from backend.models import DBOffer

class ApprovalManager:
    """
    Manages Human-in-the-Loop policy and safety guardrails for financial commitments.
    """

    def requires_approval(
        self,
        offer: Optional[DBOffer],
        configured_threshold: float = 5000.0
    ) -> bool:
        """
        Policy:
        < $500: Auto-approved
        $500 - threshold: Optional approval
        > threshold (default $5,000): Mandatory Human-in-the-loop pause
        """
        if not offer:
            return False
        return offer.total_price >= configured_threshold

    def generate_approval_summary(self, offer: DBOffer, original_budget: float) -> dict:
        savings = max(0.0, original_budget - offer.total_price)
        return {
            "supplier_name": offer.supplier_name,
            "supplier_phone": offer.supplier_phone,
            "quantity": offer.quantity_available,
            "unit_price": offer.unit_price,
            "total_price": offer.total_price,
            "original_budget": original_budget,
            "savings": savings,
            "delivery_days": offer.delivery_days,
            "delivery_date": offer.delivery_date or f"{offer.delivery_days} business days",
            "warranty_years": offer.warranty_years,
            "payment_terms": offer.payment_terms or "Standard Commercial",
            "notes": offer.notes,
            "reasoning": (
                f"{offer.supplier_name} offers the best balance of price (${offer.total_price:,.2f}), "
                f"immediate delivery ({offer.delivery_days} days), and warranty ({offer.warranty_years} yrs). "
                f"Requires your authorization to place the binding purchase order."
            )
        }

approval_manager = ApprovalManager()
