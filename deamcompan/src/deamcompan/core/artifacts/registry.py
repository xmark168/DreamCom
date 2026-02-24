"""Decision registry for tracking and querying decisions."""

from datetime import datetime
from typing import Any

from .models import Decision, DecisionStatus
from .store import ArtifactStore


class DecisionRegistry:
    """Registry for managing decisions."""

    def __init__(self, store: ArtifactStore | None = None):
        self.store = store or ArtifactStore()

    def register(self, decision: Decision) -> None:
        """Register a new decision."""
        self.store.save("decision", decision.id, decision)

    def get(self, decision_id: str) -> Decision | None:
        """Get a decision by ID."""
        return self.store.load("decision", decision_id, Decision)

    def update_status(
        self,
        decision_id: str,
        status: DecisionStatus,
        approved_by: str | None = None,
    ) -> Decision | None:
        """Update the status of a decision."""
        decision = self.get(decision_id)
        if not decision:
            return None

        decision.status = status
        decision.updated_at = datetime.utcnow()
        if approved_by:
            decision.approved_by = approved_by

        self.store.save("decision", decision.id, decision)
        return decision

    def list_all(self) -> list[Decision]:
        """List all decisions."""
        return self.store.list_all("decision", Decision)

    def list_by_status(self, status: DecisionStatus) -> list[Decision]:
        """List decisions by status."""
        all_decisions = self.list_all()
        return [d for d in all_decisions if d.status == status]

    def list_pending(self) -> list[Decision]:
        """List pending decisions."""
        return self.list_by_status(DecisionStatus.PENDING)

    def list_proposed(self) -> list[Decision]:
        """List proposed decisions."""
        return self.list_by_status(DecisionStatus.PROPOSED)

    def list_approved(self) -> list[Decision]:
        """List approved decisions."""
        return self.list_by_status(DecisionStatus.APPROVED)

    def get_metrics(self) -> dict[str, Any]:
        """Get decision metrics."""
        all_decisions = self.list_all()
        if not all_decisions:
            return {
                "total": 0,
                "by_status": {},
                "approval_rate": 0.0,
            }

        by_status = {}
        for d in all_decisions:
            by_status[d.status] = by_status.get(d.status, 0) + 1

        approved = by_status.get(DecisionStatus.APPROVED, 0)
        decided = approved + by_status.get(DecisionStatus.REJECTED, 0)
        approval_rate = approved / decided if decided > 0 else 0.0

        return {
            "total": len(all_decisions),
            "by_status": by_status,
            "approval_rate": approval_rate,
        }
