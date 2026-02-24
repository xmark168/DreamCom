"""API routes for artifacts."""

from fastapi import APIRouter, HTTPException

from core.artifacts.models import ActionItem, Decision, Initiative, MeetingLog
from api.main import registry, store

router = APIRouter()


@router.get("/decisions")
async def list_decisions():
    """List all decisions."""
    decisions = registry.list_all()
    return [d.model_dump() for d in decisions]


@router.get("/decisions/{decision_id}")
async def get_decision(decision_id: str):
    """Get a specific decision."""
    decision = registry.get(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decision.model_dump()


@router.post("/decisions/{decision_id}/approve")
async def approve_decision(decision_id: str, approved_by: str = "user"):
    """Approve a decision."""
    from core.artifacts.models import DecisionStatus

    decision = registry.update_status(decision_id, DecisionStatus.APPROVED, approved_by)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decision.model_dump()


@router.get("/action-items")
async def list_action_items():
    """List all action items."""
    actions = store.list_all("action_item", ActionItem)
    return [a.model_dump() for a in actions]


@router.get("/initiatives")
async def list_initiatives():
    """List all initiatives."""
    initiatives = store.list_all("initiative", Initiative)
    return [i.model_dump() for i in initiatives]


@router.post("/initiatives")
async def create_initiative(initiative: Initiative):
    """Create a new initiative."""
    store.save("initiative", initiative.id, initiative)
    return initiative.model_dump()
