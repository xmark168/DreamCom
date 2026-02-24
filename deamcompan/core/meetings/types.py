"""Types and enums for meetings."""

from enum import Enum


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


class MeetingStatus(str, Enum):
    """Status of a meeting."""

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
