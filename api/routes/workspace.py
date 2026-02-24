"""API routes for workspace."""

from fastapi import APIRouter

from api.main import workspace

router = APIRouter()


@router.get("/snapshot")
async def get_snapshot():
    """Get current workspace snapshot."""
    if not workspace:
        return {"error": "Workspace not initialized"}

    snapshot = workspace.get_snapshot()
    return snapshot.model_dump()


@router.get("/metrics")
async def get_metrics():
    """Get workspace metrics."""
    if not workspace:
        return {"error": "Workspace not initialized"}

    return workspace.get_metrics()


@router.get("/agents")
async def get_workspace_agents():
    """Get agents in workspace."""
    if not workspace:
        return {"error": "Workspace not initialized"}

    return [
        {"id": a.id, "role": a.role, "name": a.name}
        for a in workspace.agents.values()
    ]
