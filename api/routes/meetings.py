"""API routes for meetings."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.meetings.engine import MeetingEngine
from core.meetings.types import MeetingType
from api.main import workspace
from api.routes.agents import _agent_registry

router = APIRouter()

_meeting_engine: MeetingEngine | None = None


def _get_engine() -> MeetingEngine:
    global _meeting_engine
    if _meeting_engine is None:
        from api.main import store
        _meeting_engine = MeetingEngine(store)
    return _meeting_engine


class MeetingCreateRequest(BaseModel):
    title: str
    meeting_type: str
    agenda: list[str]
    participant_ids: list[str]


class MeetingCreateResponse(BaseModel):
    meeting_id: str
    title: str
    status: str


@router.post("/create", response_model=MeetingCreateResponse)
async def create_meeting(request: MeetingCreateRequest):
    """Create a new meeting."""
    engine = _get_engine()

    # Get participants
    participants = []
    for pid in request.participant_ids:
        agent = _agent_registry.get(pid)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {pid} not found")
        participants.append(agent)

    try:
        meeting_type = MeetingType(request.meeting_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid meeting type: {request.meeting_type}")

    context = await engine.create_meeting(
        title=request.title,
        meeting_type=meeting_type,
        agenda=request.agenda,
        participants=participants,
    )

    return MeetingCreateResponse(
        meeting_id=context.meeting_id,
        title=context.title,
        status=context.status.value,
    )


@router.post("/{meeting_id}/run")
async def run_meeting(meeting_id: str):
    """Run a meeting."""
    engine = _get_engine()

    try:
        result = await engine.run_meeting(meeting_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{meeting_id}")
async def get_meeting(meeting_id: str):
    """Get meeting details."""
    from core.artifacts.models import MeetingLog
    from api.main import store

    meeting = store.load("meeting", meeting_id, MeetingLog)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return meeting.model_dump()


@router.get("/list")
async def list_meetings():
    """List all meetings."""
    from core.artifacts.models import MeetingLog
    from api.main import store

    meetings = store.list_all("meeting", MeetingLog)
    return [m.model_dump() for m in meetings]
