"""Meeting phases for hybrid async/sync coordination."""

import uuid
from typing import TYPE_CHECKING, Any

from ..artifacts.models import AgentThought
from .types import MeetingPhase

if TYPE_CHECKING:
    from .engine import MeetingContext


class AsyncPrepPhase:
    """Async preparation phase where agents prepare their inputs independently."""

    def __init__(self, context: "MeetingContext"):
        self.context = context
        self.prep_results: dict[str, Any] = {}

    async def run(self) -> dict[str, Any]:
        """Run async preparation for all participants."""
        agenda = self.context.agenda
        participants = self.context.participants

        # Each participant prepares their input asynchronously
        for participant in participants:
            if hasattr(participant, "think"):
                prompt = self._build_prep_prompt(participant, agenda)
                try:
                    response = await participant.think(prompt)
                    self.prep_results[participant.id] = {
                        "agent_id": participant.id,
                        "agent_role": participant.role,
                        "agent_name": participant.name,
                        "preparation": response,
                    }
                    participant.add_thought(
                        f"Prepared for meeting: {self.context.title}",
                        meeting_id=self.context.meeting_id,
                    )
                except Exception as e:
                    self.prep_results[participant.id] = {
                        "agent_id": participant.id,
                        "agent_role": participant.role,
                        "agent_name": participant.name,
                        "error": str(e),
                    }

        return {
            "phase": MeetingPhase.ASYNC_PREP,
            "prep_results": self.prep_results,
        }

    def _build_prep_prompt(self, participant, agenda: list[str]) -> str:
        """Build preparation prompt for a participant."""
        return f"""You are preparing for a meeting: "{self.context.title}"

Your role: {participant.role}
Meeting type: {self.context.meeting_type}

Agenda items:
{chr(10).join(f"- {item}" for item in agenda)}

Please prepare:
1. KEY_POINTS: [What you want to communicate]
2. RECOMMENDATIONS: [Your suggested actions]
3. CONCERNS: [Risks or issues to raise]
4. QUESTIONS: [What you need clarified]
5. DATA: [Facts or analysis to share]

Be concise but thorough. Your preparation will be shared with other participants.
"""


class SyncDecisionPhase:
    """Synchronous decision phase with round-robin discussion."""

    def __init__(self, context: "MeetingContext"):
        self.context = context
        self.discussion_log: list[AgentThought] = []
        self.decisions: list[dict[str, Any]] = []
        self.action_items: list[dict[str, Any]] = []

    async def run(self, prep_results: dict[str, Any]) -> dict[str, Any]:
        """Run synchronous decision phase."""
        participants = self.context.participants

        # Round-robin discussion
        discussion_context = self._build_discussion_context(prep_results)

        for round_num in range(2):  # 2 rounds of discussion
            for participant in participants:
                if hasattr(participant, "think"):
                    prompt = self._build_discussion_prompt(
                        participant,
                        discussion_context,
                        round_num,
                    )
                    try:
                        response = await participant.think(prompt)
                        thought = AgentThought(
                            agent_id=participant.id,
                            agent_role=participant.role,
                            content=response,
                            meeting_id=self.context.meeting_id,
                        )
                        self.discussion_log.append(thought)
                        participant.add_thought(
                            f"Spoke in meeting round {round_num + 1}",
                            meeting_id=self.context.meeting_id,
                        )
                        discussion_context += f"\n\n{participant.name}: {response}"
                    except Exception as e:
                        discussion_context += f"\n\n{participant.name}: [Error: {e}]"

        # Final synthesis by CEO or designated facilitator
        facilitator = self._get_facilitator()
        if facilitator and hasattr(facilitator, "think"):
            synthesis = await self._synthesize(facilitator, discussion_context)
            self._extract_decisions_and_actions(synthesis)

        return {
            "phase": MeetingPhase.SYNC_DECISION,
            "discussion_log": [
                {
                    "agent_id": t.agent_id,
                    "agent_role": t.agent_role,
                    "content": t.content,
                    "timestamp": t.timestamp.isoformat(),
                }
                for t in self.discussion_log
            ],
            "decisions": self.decisions,
            "action_items": self.action_items,
        }

    def _build_discussion_context(self, prep_results: dict[str, Any]) -> str:
        """Build context from preparation results."""
        context = f"Meeting: {self.context.title}\n\nPreparations:\n"
        for agent_id, result in prep_results.items():
            if "preparation" in result:
                context += f"\n{result['agent_name']} ({result['agent_role']}):\n{result['preparation']}\n"
        return context

    def _build_discussion_prompt(
        self,
        participant,
        discussion_context: str,
        round_num: int,
    ) -> str:
        """Build discussion prompt for a participant."""
        round_focus = [
            "Share your perspective and react to others' inputs",
            "Focus on converging toward decisions and addressing disagreements",
        ]

        return f"""You are in a meeting: "{self.context.title}"
Your role: {participant.role}
Round: {round_num + 1} of 2

Discussion so far:
{discussion_context}

This round, focus on: {round_focus[round_num]}

Provide your contribution:
1. REACTION: [Your response to what others said]
2. POSITION: [Your stance on key issues]
3. PROPOSAL: [Specific suggestions]
4. CONCERNS: [Any remaining issues]

Be constructive and aim for progress toward decisions.
"""

    def _get_facilitator(self):
        """Get the meeting facilitator (CEO or first participant)."""
        for p in self.context.participants:
            if p.role == "CEO":
                return p
        return self.context.participants[0] if self.context.participants else None

    async def _synthesize(self, facilitator, discussion_context: str) -> str:
        """Have facilitator synthesize the discussion."""
        prompt = f"""As the meeting facilitator, synthesize the following discussion and produce clear outputs.

Meeting: {self.context.title}
Agenda: {self.context.agenda}

Discussion:
{discussion_context}

Provide:
1. SUMMARY: [Brief summary of key points discussed]
2. DECISIONS: [Clear decisions made - format as "DECISION: [description]"]
3. ACTION_ITEMS: [Specific tasks - format as "ACTION: [description] | OWNER: [role] | DEADLINE: [when]"]
4. OPEN_QUESTIONS: [Issues not resolved]
5. NEXT_STEPS: [What happens next]
"""
        return await facilitator.think(prompt)

    def _extract_decisions_and_actions(self, synthesis: str) -> None:
        """Extract structured decisions and action items from synthesis."""
        lines = synthesis.split("\n")

        for line in lines:
            line = line.strip()
            if line.startswith("DECISION:") or line.startswith("2. DECISION:"):
                decision_text = line.split(":", 1)[1].strip() if ":" in line else line
                self.decisions.append({
                    "id": str(uuid.uuid4())[:8],
                    "description": decision_text,
                    "status": "proposed",
                })
            elif line.startswith("ACTION:") or line.startswith("3. ACTION:"):
                action_text = line.split(":", 1)[1].strip() if ":" in line else line
                # Parse owner and deadline if present
                owner = "TBD"
                deadline = "TBD"
                if "| OWNER:" in action_text:
                    parts = action_text.split("| OWNER:")
                    action_desc = parts[0].strip()
                    rest = parts[1]
                    if "| DEADLINE:" in rest:
                        owner = rest.split("| DEADLINE:")[0].strip()
                        deadline = rest.split("| DEADLINE:")[1].strip()
                    else:
                        owner = rest.strip()
                else:
                    action_desc = action_text

                self.action_items.append({
                    "id": str(uuid.uuid4())[:8],
                    "description": action_desc,
                    "owner": owner,
                    "deadline": deadline,
                    "status": "todo",
                })
