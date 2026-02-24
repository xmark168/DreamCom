"""Pydantic models for artifacts in DeamCompan."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DecisionStatus(str, Enum):
    """Status of a decision."""

    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    PENDING = "pending"


class ActionItemStatus(str, Enum):
    """Status of an action item."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class MeetingType(str, Enum):
    """Types of meetings."""

    EXECUTIVE_REVIEW = "executive_review"
    BOARD_REVIEW = "board_review"
    DECISION_MEETING = "decision_meeting"
    TEAM_CHECKIN = "team_checkin"


class MeetingPhase(str, Enum):
    """Phases of a meeting."""

    ASYNC_PREP = "async_prep"
    SYNC_DECISION = "sync_decision"
    COMPLETED = "completed"


class Decision(BaseModel):
    """A decision made in the organization."""

    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Decision title")
    description: str = Field(..., description="Detailed description")
    rationale: str = Field(..., description="Why this decision was made")
    alternatives: list[str] = Field(default_factory=list, description="Alternatives considered")
    expected_outcomes: list[str] = Field(default_factory=list, description="Expected outcomes")
    status: DecisionStatus = Field(default=DecisionStatus.PROPOSED)
    proposed_by: str = Field(..., description="Agent/user who proposed")
    approved_by: str | None = Field(default=None, description="Who approved")
    meeting_id: str | None = Field(default=None, description="Associated meeting")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ActionItem(BaseModel):
    """An action item from a meeting."""

    id: str = Field(..., description="Unique identifier")
    description: str = Field(..., description="What needs to be done")
    owner: str = Field(..., description="Who is responsible")
    deadline: datetime | None = Field(default=None)
    status: ActionItemStatus = Field(default=ActionItemStatus.TODO)
    meeting_id: str = Field(..., description="Source meeting")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MeetingLog(BaseModel):
    """Log of a meeting."""

    id: str = Field(..., description="Unique identifier")
    meeting_type: MeetingType
    title: str
    agenda: list[str] = Field(default_factory=list)
    participants: list[str] = Field(default_factory=list)
    phase: MeetingPhase = Field(default=MeetingPhase.ASYNC_PREP)
    decisions: list[str] = Field(default_factory=list, description="Decision IDs")
    action_items: list[str] = Field(default_factory=list, description="Action item IDs")
    discussion_summary: str = Field(default="")
    open_questions: list[str] = Field(default_factory=list)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = Field(default=None)


class Initiative(BaseModel):
    """A strategic initiative or project."""

    id: str = Field(..., description="Unique identifier")
    name: str
    description: str
    owner: str = Field(..., description="Team/lead responsible")
    status: str = Field(default="active")
    backlog: list[str] = Field(default_factory=list, description="Task/action IDs")
    risks: list[str] = Field(default_factory=list)
    milestones: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AgentThought(BaseModel):
    """An agent's thought or contribution."""

    agent_id: str
    agent_role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    meeting_id: str | None = None


class WorkspaceSnapshot(BaseModel):
    """Snapshot of the entire workspace state."""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    active_initiatives: list[Initiative] = Field(default_factory=list)
    pending_decisions: list[Decision] = Field(default_factory=list)
    recent_meetings: list[MeetingLog] = Field(default_factory=list)
    open_action_items: list[ActionItem] = Field(default_factory=list)
