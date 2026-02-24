"""CEO Orchestrator agent."""

from typing import Any

from .base import BaseAgent


CEO_SYSTEM_PROMPT = """You are the CEO Orchestrator of a virtual company.
Your role is to translate governance into execution and coordinate all teams.

Responsibilities:
- Translate BOD strategy into company-wide objectives
- Set priorities and allocate resources across teams
- Resolve cross-team conflicts and dependencies
- Consolidate inputs from all teams into coherent decisions
- Escalate to BOD when needed
- Ensure alignment between strategy and execution

When coordinating:
1. Listen to all perspectives
2. Identify trade-offs and conflicts
3. Make or propose clear decisions
4. Assign ownership and deadlines
5. Follow up on execution

You are the integrator - the single source of truth for priorities."""


class CEOOrchestrator(BaseAgent):
    """CEO agent for executive orchestration."""

    def __init__(self, llm_client=None, name: str = "CEO"):
        super().__init__(
            role="CEO",
            name=name,
            llm_client=llm_client,
            system_prompt=CEO_SYSTEM_PROMPT,
        )
        self.priorities: list[dict[str, Any]] = []
        self.team_status: dict[str, Any] = {}

    async def act(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute a CEO task."""
        action = task.get("action")

        if action == "prioritize":
            return await self._prioritize(task)
        elif action == "coordinate_meeting":
            return await self._coordinate_meeting(task)
        elif action == "resolve_conflict":
            return await self._resolve_conflict(task)
        elif action == "propose_decision":
            return await self._propose_decision(task)
        elif action == "allocate_resources":
            return await self._allocate_resources(task)
        else:
            return {"error": f"Unknown action: {action}"}

    async def _prioritize(self, task: dict[str, Any]) -> dict[str, Any]:
        """Prioritize initiatives based on strategy and constraints."""
        initiatives = task.get("initiatives", [])
        strategy = task.get("strategy", "")
        constraints = task.get("constraints", {})

        prompt = f"""Prioritize the following initiatives:

Strategy: {strategy}
Constraints: {constraints}
Initiatives: {initiatives}

Provide:
1. RANKED_LIST: [Ordered by priority with rationale]
2. RESOURCE_ALLOCATION: [How to distribute resources]
3. DEPENDENCIES: [Key dependencies between initiatives]
4. TIMELINE: [Suggested sequence and timing]
"""
        response = await self.think(prompt)
        self.add_thought("Prioritized initiatives")

        return {
            "action": "prioritize",
            "priorities": response,
        }

    async def _coordinate_meeting(self, task: dict[str, Any]) -> dict[str, Any]:
        """Coordinate a cross-team meeting."""
        meeting_type = task.get("meeting_type", "executive_review")
        participants = task.get("participants", [])
        agenda = task.get("agenda", [])

        prompt = f"""Coordinate a {meeting_type} meeting with participants: {participants}

Agenda items: {agenda}

Provide:
1. MEETING_STRUCTURE: [How to run the meeting efficiently]
2. KEY_QUESTIONS: [Critical questions to address]
3. DECISION_POINTS: [What needs to be decided]
4. EXPECTED_OUTCOMES: [What should be achieved]
"""
        response = await self.think(prompt)
        self.add_thought(f"Coordinated {meeting_type} meeting")

        return {
            "action": "coordinate_meeting",
            "meeting_type": meeting_type,
            "coordination_plan": response,
        }

    async def _resolve_conflict(self, task: dict[str, Any]) -> dict[str, Any]:
        """Resolve a conflict between teams or priorities."""
        conflict = task.get("conflict", {})
        parties = task.get("parties", [])

        prompt = f"""Resolve the following conflict:

Parties involved: {parties}
Conflict description: {conflict}

Provide:
1. ROOT_CAUSE: [Underlying issue]
2. OPTIONS: [Possible resolutions]
3. RECOMMENDATION: [Best path forward with rationale]
4. NEXT_STEPS: [Specific actions for each party]
"""
        response = await self.think(prompt)
        self.add_thought("Resolved conflict")

        return {
            "action": "resolve_conflict",
            "resolution": response,
        }

    async def _propose_decision(self, task: dict[str, Any]) -> dict[str, Any]:
        """Propose a decision to the BOD."""
        topic = task.get("topic", "")
        options = task.get("options", [])
        context = task.get("context", {})

        prompt = f"""Propose a decision on: {topic}

Options considered: {options}
Context: {context}

Provide a formal decision proposal with:
1. TITLE: [Clear decision statement]
2. DESCRIPTION: [What is being decided]
3. RATIONALE: [Why this is the right choice]
4. ALTERNATIVES: [Other options and why rejected]
5. EXPECTED_OUTCOMES: [What will happen if approved]
6. RISKS: [Potential downsides and mitigations]
"""
        response = await self.think(prompt)
        self.add_thought(f"Proposed decision: {topic}")

        return {
            "action": "propose_decision",
            "proposal": response,
            "topic": topic,
        }

    async def _allocate_resources(self, task: dict[str, Any]) -> dict[str, Any]:
        """Allocate resources across teams/initiatives."""
        available = task.get("available_resources", {})
        requests = task.get("requests", [])
        priorities = task.get("priorities", [])

        prompt = f"""Allocate resources:

Available: {available}
Requests: {requests}
Priorities: {priorities}

Provide:
1. ALLOCATION: [Specific allocation per request]
2. RATIONALE: [Why allocated this way]
3. TRADE_OFFS: [What had to be sacrificed]
4. CONTINGENCY: [Backup plans if needs change]
"""
        response = await self.think(prompt)
        self.add_thought("Allocated resources")

        return {
            "action": "allocate_resources",
            "allocation": response,
        }
