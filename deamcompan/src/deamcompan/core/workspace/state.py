"""Workspace state management."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from ..artifacts.models import (
    ActionItem,
    Decision,
    Initiative,
    MeetingLog,
    WorkspaceSnapshot,
)
from ..artifacts.registry import DecisionRegistry
from ..artifacts.store import ArtifactStore

if TYPE_CHECKING:
    from ..agents.base import BaseAgent


class WorkspaceState:
    """Current state of the workspace."""

    def __init__(self, store: Optional[ArtifactStore] = None):
        self.store = store or ArtifactStore()
        self.decision_registry = DecisionRegistry(self.store)
        self.active_initiatives: list[Initiative] = []
        self.active_meetings: list[MeetingLog] = []
        self.pending_decisions: list[Decision] = []
        self.open_action_items: list[ActionItem] = []
        self.agents: dict[str, "BaseAgent"] = {}
        self._load_state()

    def _load_state(self) -> None:
        """Load current state from store."""
        self.active_initiatives = self.store.list_all("initiative", Initiative)
        self.active_meetings = [
            m for m in self.store.list_all("meeting", MeetingLog)
            if not m.completed_at
        ]
        self.pending_decisions = self.decision_registry.list_pending()
        self.open_action_items = [
            a for a in self.store.list_all("action_item", ActionItem)
            if a.status in ["todo", "in_progress"]
        ]

    def register_agent(self, agent: "BaseAgent") -> None:
        """Register an agent in the workspace."""
        self.agents[agent.id] = agent

    def get_agent(self, agent_id: str) -> Optional["BaseAgent"]:
        """Get an agent by ID."""
        return self.agents.get(agent_id)

    def get_agents_by_role(self, role: str) -> list["BaseAgent"]:
        """Get all agents with a specific role."""
        return [a for a in self.agents.values() if a.role == role]

    def add_initiative(self, initiative: Initiative) -> None:
        """Add a new initiative."""
        self.active_initiatives.append(initiative)
        self.store.save("initiative", initiative.id, initiative)

    def get_initiative(self, initiative_id: str) -> Optional[Initiative]:
        """Get an initiative by ID."""
        for i in self.active_initiatives:
            if i.id == initiative_id:
                return i
        return self.store.load("initiative", initiative_id, Initiative)

    def get_snapshot(self) -> WorkspaceSnapshot:
        """Get a snapshot of the current workspace state."""
        return WorkspaceSnapshot(
            active_initiatives=self.active_initiatives,
            pending_decisions=self.pending_decisions,
            recent_meetings=sorted(
                self.store.list_all("meeting", MeetingLog),
                key=lambda m: m.started_at,
                reverse=True,
            )[:10],
            open_action_items=self.open_action_items,
        )

    def get_metrics(self) -> dict[str, Any]:
        """Get workspace metrics."""
        all_decisions = self.decision_registry.list_all()
        all_meetings = self.store.list_all("meeting", MeetingLog)
        all_actions = self.store.list_all("action_item", ActionItem)

        completed_meetings = [m for m in all_meetings if m.completed_at]

        return {
            "agents": len(self.agents),
            "active_initiatives": len(self.active_initiatives),
            "total_meetings": len(all_meetings),
            "completed_meetings": len(completed_meetings),
            "total_decisions": len(all_decisions),
            "pending_decisions": len(self.pending_decisions),
            "total_action_items": len(all_actions),
            "open_action_items": len(self.open_action_items),
            "decision_metrics": self.decision_registry.get_metrics(),
        }
