"""Meeting engine for orchestrating hybrid async/sync meetings."""

import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..artifacts.models import (
    ActionItem,
    ActionItemStatus,
    Decision,
    DecisionStatus,
    MeetingLog,
    MeetingPhase as ModelMeetingPhase,
    MeetingType as ModelMeetingType,
)
from ..artifacts.store import ArtifactStore
from .phases import AsyncPrepPhase, SyncDecisionPhase
from .types import MeetingPhase, MeetingStatus, MeetingType

if TYPE_CHECKING:
    from ..agents.base import BaseAgent


@dataclass
class MeetingContext:
    """Context for a meeting."""

    meeting_id: str
    title: str
    meeting_type: MeetingType
    agenda: list[str]
    participants: list = field(default_factory=list)
    status: MeetingStatus = MeetingStatus.SCHEDULED
    current_phase: MeetingPhase = MeetingPhase.ASYNC_PREP


class MeetingEngine:
    """Engine for running meetings."""

    def __init__(self, store: ArtifactStore | None = None):
        self.store = store or ArtifactStore()
        self.active_meetings: dict[str, MeetingContext] = {}

    async def create_meeting(
        self,
        title: str,
        meeting_type: MeetingType,
        agenda: list[str],
        participants: list["BaseAgent"],
    ) -> MeetingContext:
        """Create a new meeting."""
        meeting_id = str(uuid.uuid4())[:8]

        context = MeetingContext(
            meeting_id=meeting_id,
            title=title,
            meeting_type=meeting_type,
            agenda=agenda,
            participants=participants,
            status=MeetingStatus.SCHEDULED,
            current_phase=MeetingPhase.ASYNC_PREP,
        )

        self.active_meetings[meeting_id] = context

        # Create initial meeting log
        log = MeetingLog(
            id=meeting_id,
            meeting_type=ModelMeetingType(meeting_type.value),
            title=title,
            agenda=agenda,
            participants=[p.name for p in participants],
            phase=ModelMeetingPhase.ASYNC_PREP,
        )
        self.store.save("meeting", meeting_id, log)

        return context

    async def run_meeting(self, meeting_id: str) -> dict[str, Any]:
        """Run a complete meeting through all phases."""
        context = self.active_meetings.get(meeting_id)
        if not context:
            return {"error": f"Meeting {meeting_id} not found"}

        # Phase 1: Async Prep
        context.status = MeetingStatus.IN_PROGRESS
        context.current_phase = MeetingPhase.ASYNC_PREP

        prep_phase = AsyncPrepPhase(context)
        prep_results = await prep_phase.run()

        # Phase 2: Sync Decision
        context.current_phase = MeetingPhase.SYNC_DECISION

        decision_phase = SyncDecisionPhase(context)
        decision_results = await decision_phase.run(prep_results["prep_results"])

        # Complete meeting
        context.status = MeetingStatus.COMPLETED
        context.current_phase = MeetingPhase.COMPLETED

        # Update meeting log
        log = self.store.load("meeting", meeting_id, MeetingLog)
        if log:
            log.phase = ModelMeetingPhase.COMPLETED
            log.decisions = [d["id"] for d in decision_results["decisions"]]
            log.action_items = [a["id"] for a in decision_results["action_items"]]
            log.discussion_summary = self._summarize_discussion(
                decision_results["discussion_log"]
            )
            log.completed_at = __import__("datetime").datetime.utcnow()
            self.store.save("meeting", meeting_id, log)

        # Save decisions
        for decision_data in decision_results["decisions"]:
            decision = Decision(
                id=decision_data["id"],
                title=decision_data["description"][:50],
                description=decision_data["description"],
                rationale="Discussed and decided in meeting",
                status=DecisionStatus.PROPOSED,
                proposed_by="meeting",
                meeting_id=meeting_id,
            )
            self.store.save("decision", decision.id, decision)

        # Save action items
        for action_data in decision_results["action_items"]:
            action = ActionItem(
                id=action_data["id"],
                description=action_data["description"],
                owner=action_data["owner"],
                status=ActionItemStatus.TODO,
                meeting_id=meeting_id,
            )
            self.store.save("action_item", action.id, action)

        return {
            "meeting_id": meeting_id,
            "title": context.title,
            "prep_results": prep_results,
            "decision_results": decision_results,
            "status": "completed",
        }

    def _summarize_discussion(self, discussion_log: list[dict]) -> str:
        """Create a brief summary of the discussion."""
        if not discussion_log:
            return "No discussion recorded"

        # Simple summary: count contributions by role
        role_counts = {}
        for entry in discussion_log:
            role = entry.get("agent_role", "Unknown")
            role_counts[role] = role_counts.get(role, 0) + 1

        summary = "Discussion involved: " + ", ".join(
            f"{role} ({count} contributions)" for role, count in role_counts.items()
        )
        return summary

    def get_meeting(self, meeting_id: str) -> MeetingContext | None:
        """Get a meeting context by ID."""
        return self.active_meetings.get(meeting_id)

    def list_active_meetings(self) -> list[MeetingContext]:
        """List all active meetings."""
        return [
            ctx for ctx in self.active_meetings.values()
            if ctx.status != MeetingStatus.COMPLETED
        ]
