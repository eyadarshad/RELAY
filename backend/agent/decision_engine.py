from typing import List, Dict, Any, Tuple
from backend.models import DBOffer, OfferStatus

DEFAULT_WEIGHTS = {
    "price": 0.35,
    "delivery": 0.25,
    "availability": 0.20,
    "warranty": 0.10,
    "reliability": 0.10
}

class DecisionEngine:
    """
    Multi-criteria decision engine for ranking supplier offers and generating transparent explanations.
    """

    def evaluate_offers(
        self,
        offers: List[DBOffer],
        target_budget: float,
        required_quantity: int,
        max_delivery_days: int = 4,
        weights: Dict[str, float] = None
    ) -> Tuple[List[DBOffer], str]:
        if not offers:
            return [], "No supplier offers collected."

        w = weights or DEFAULT_WEIGHTS

        for offer in offers:
            score = 0.0

            # 1. Price Score (0 - 1.0)
            if offer.total_price > 0 and target_budget > 0:
                if offer.total_price <= target_budget:
                    # Cheaper than budget earns higher score
                    price_ratio = 1.0 - ((offer.total_price - (target_budget * 0.7)) / (target_budget * 0.3))
                    price_score = max(0.5, min(1.0, price_ratio))
                else:
                    # Over budget penalty
                    over_pct = (offer.total_price - target_budget) / target_budget
                    price_score = max(0.0, 0.4 - (over_pct * 2.0))
            else:
                price_score = 0.5
            score += price_score * w["price"]

            # 2. Delivery Score (0 - 1.0)
            days = offer.delivery_days or 5
            if days <= max_delivery_days:
                deliv_score = 1.0 - ((days - 1) / max(1, max_delivery_days)) * 0.3
            else:
                deliv_score = max(0.1, 0.5 - ((days - max_delivery_days) * 0.2))
            score += deliv_score * w["delivery"]

            # 3. Availability Score (0 - 1.0)
            if offer.quantity_available >= required_quantity:
                avail_score = 1.0
            else:
                avail_score = max(0.0, offer.quantity_available / max(1, required_quantity))
            score += avail_score * w["availability"]

            # 4. Warranty Score (0 - 1.0)
            w_years = offer.warranty_years or 0.0
            warranty_score = min(1.0, w_years / 2.0)
            score += warranty_score * w["warranty"]

            # 5. Reliability Score (0 - 1.0)
            reliability_score = 0.90
            score += reliability_score * w["reliability"]

            offer.composite_score = round(score * 100, 1)

            # Auto-reject disqualified offers
            if offer.quantity_available < required_quantity:
                offer.status = OfferStatus.REJECTED.value
                offer.notes = f"Disqualified: Insufficient quantity ({offer.quantity_available}/{required_quantity} units available)."
            elif offer.total_price > target_budget * 1.15:
                offer.status = OfferStatus.REJECTED.value
                offer.notes = f"Disqualified: Price exceeds budget ceiling by over 15% (${offer.total_price:,.2f})."
            else:
                offer.status = OfferStatus.CANDIDATE.value

        # Sort offers by composite score descending
        valid_offers = [o for o in offers if o.status != OfferStatus.REJECTED.value]
        valid_offers.sort(key=lambda o: o.composite_score, reverse=True)

        if valid_offers:
            best_offer = valid_offers[0]
            best_offer.status = OfferStatus.BEST.value

            # Generate natural language reasoning
            savings = target_budget - best_offer.total_price
            reasoning = (
                f"{best_offer.supplier_name} is ranked #1 (Score: {best_offer.composite_score}/100). "
                f"They meet the full volume of {best_offer.quantity_available} units, deliver in {best_offer.delivery_days} days "
                f"before deadline, provide a {best_offer.warranty_years}-year warranty, and total cost is "
                f"${best_offer.total_price:,.2f} "
                f"({'saving $' + f'{savings:,.2f}' if savings > 0 else 'within target budget'})."
            )
        else:
            reasoning = "All evaluated suppliers had stock shortages or exceeded budget constraints."

        return offers, reasoning

decision_engine = DecisionEngine()
