import json
import os
from typing import List
from backend.models import Supplier, WorkflowType

SUPPLIERS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "suppliers.json")

class SupplierDiscoveryService:
    def __init__(self):
        self._suppliers: List[Supplier] = []
        self._load_suppliers()

    def _load_suppliers(self):
        if os.path.exists(SUPPLIERS_FILE):
            with open(SUPPLIERS_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
                self._suppliers = [Supplier(**item) for item in raw]
        else:
            self._suppliers = []

    def get_all_suppliers(self) -> List[Supplier]:
        return self._suppliers

    def discover_for_mission(
        self,
        workflow_type: WorkflowType,
        item: str = "",
        location: str = "",
        limit: int = 4
    ) -> List[Supplier]:
        """
        Discovers and ranks candidate suppliers for the given mission.
        """
        candidates: List[Supplier] = []

        if workflow_type == WorkflowType.PROCURE:
            # Match office furniture / chair suppliers
            for s in self._suppliers:
                if s.category == "office_furniture":
                    candidates.append(s)

        elif workflow_type == WorkflowType.RESCUE:
            for s in self._suppliers:
                if s.category == "logistics_rescue":
                    candidates.append(s)

        elif workflow_type == WorkflowType.QUOTE:
            for s in self._suppliers:
                if s.category == "commercial_generators":
                    candidates.append(s)

        elif workflow_type == WorkflowType.SCHEDULE:
            for s in self._suppliers:
                if s.category == "waitlist_schedule":
                    candidates.append(s)

        # If no specific category matched, fallback to matching keywords
        if not candidates:
            item_lower = (item or "").lower()
            for s in self._suppliers:
                if any(item_lower in p.lower() for p in s.products) or item_lower in s.category.lower():
                    candidates.append(s)

        # Sort by reliability score descending
        candidates.sort(key=lambda s: s.reliability_score, reverse=True)
        return candidates[:limit]

discovery_service = SupplierDiscoveryService()
