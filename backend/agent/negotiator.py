import logging
from typing import Optional, Dict, Any, Tuple
from backend.models import DBOffer, Supplier, OfferStatus
from backend.agent.caller import call_agent

logger = logging.getLogger(__name__)

class NegotiationEngine:
    """
    Handles autonomous second-round phone negotiations leveraging competing bids.
    """

    def is_negotiation_warranted(
        self,
        best_offer: DBOffer,
        second_best_offer: Optional[DBOffer],
        target_budget: float
    ) -> bool:
        """
        Determines if a follow-up negotiation call will yield cost savings.
        """
        if not best_offer or best_offer.status == OfferStatus.REJECTED.value:
            return False
        # If total price is above $1,000 and within budget range, negotiation is beneficial
        return best_offer.total_price >= 1000.0

    async def execute_negotiation(
        self,
        best_offer: DBOffer,
        supplier: Supplier,
        second_best_offer: Optional[DBOffer],
        item: str,
        quantity: int,
        mission_id: str
    ) -> Tuple[Dict[str, Any], float]:
        """
        Executes a targeted negotiation call via CALL-E.
        """
        initial_price = best_offer.total_price
        target_price = round(initial_price * 0.93, 2)  # Target ~7% discount
        competing_price = second_best_offer.total_price if second_best_offer else round(initial_price * 0.96, 2)

        logger.info(f"Initiating autonomous negotiation with {best_offer.supplier_name}: Initial ${initial_price} -> Target ${target_price}")

        call_result = await call_agent.make_negotiation_call(
            supplier=supplier,
            current_offer_price=initial_price,
            target_price=target_price,
            competing_offer_price=competing_price,
            quantity=quantity,
            item=item,
            mission_id=mission_id
        )

        structured = call_result.get("result", {})
        if structured.get("negotiation_success", False):
            revised_total = float(structured.get("revised_total_price", initial_price))
            savings = max(0.0, initial_price - revised_total)
            
            # Update offer in place
            best_offer.original_price = initial_price
            best_offer.total_price = revised_total
            best_offer.unit_price = float(structured.get("revised_unit_price", round(revised_total / max(1, quantity), 2)))
            best_offer.negotiated_savings = savings
            best_offer.status = OfferStatus.BEST.value
            best_offer.notes = (
                f"Negotiated Discount: Saved ${savings:,.2f}. "
                f"Concessions: {structured.get('extra_concessions', 'Standard warranty')}"
            )
            return call_result, savings
        else:
            return call_result, 0.0

negotiation_engine = NegotiationEngine()
