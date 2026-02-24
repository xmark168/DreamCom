"""Board of Directors agent."""

from typing import Any

from .base import BaseAgent


BOD_SYSTEM_PROMPT = """You are the Board of Directors (BOD) of a virtual company.
Your role is governance and strategic oversight.

Responsibilities:
- Define strategic goals and long-term direction
- Approve or reject major decisions proposed by the CEO
- Enforce risk boundaries and governance policies
- Challenge assumptions and ensure accountability
- Set quarterly objectives and review progress

When making decisions:
1. Consider the strategic alignment
2. Assess risks and trade-offs
3. Evaluate expected outcomes
4. Provide clear rationale for approval/rejection
5. Suggest alternatives if rejecting

Be thorough but decisive. Your decisions shape the company's future."""


class BoardOfDirectors(BaseAgent):
    """Board of Directors agent for governance."""

    def __init__(self, llm_client=None, name: str = "Board of Directors"):
        super().__init__(
            role="BOD",
            name=name,
            llm_client=llm_client,
            system_prompt=BOD_SYSTEM_PROMPT,
        )

    async def act(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute a BOD task."""
        action = task.get("action")

        if action == "review_decision":
            return await self._review_decision(task)
        elif action == "set_strategy":
            return await self._set_strategy(task)
        elif action == "assess_risk":
            return await self._assess_risk(task)
        else:
            return {"error": f"Unknown action: {action}"}

    async def _review_decision(self, task: dict[str, Any]) -> dict[str, Any]:
        """Review a proposed decision."""
        decision = task.get("decision", {})
        prompt = f"""Review the following proposed decision:

Title: {decision.get('title', 'N/A')}
Description: {decision.get('description', 'N/A')}
Rationale: {decision.get('rationale', 'N/A')}
Alternatives: {decision.get('alternatives', [])}
Expected Outcomes: {decision.get('expected_outcomes', [])}

Provide your assessment in this format:
1. RECOMMENDATION: [APPROVE / REJECT / REQUEST_MODIFICATION]
2. RATIONALE: [Your reasoning]
3. CONCERNS: [Any risks or issues]
4. SUGGESTIONS: [Improvements if applicable]
"""
        response = await self.think(prompt)
        self.add_thought(f"Reviewed decision: {decision.get('title')}")

        return {
            "action": "review_decision",
            "decision_id": decision.get("id"),
            "assessment": response,
        }

    async def _set_strategy(self, task: dict[str, Any]) -> dict[str, Any]:
        """Set strategic goals."""
        context = task.get("context", {})
        prompt = f"""Based on the following context, define strategic goals for the company:

Current State: {context}

Provide:
1. VISION: [Long-term vision statement]
2. OBJECTIVES: [3-5 key objectives for the quarter]
3. PRIORITIES: [Ranked list of initiatives]
4. RISK_BOUNDARIES: [What to avoid or limit]
"""
        response = await self.think(prompt)
        self.add_thought("Set strategic goals")

        return {
            "action": "set_strategy",
            "strategy": response,
        }

    async def _assess_risk(self, task: dict[str, Any]) -> dict[str, Any]:
        """Assess risk of a proposal."""
        proposal = task.get("proposal", {})
        prompt = f"""Assess the risk of the following proposal:

{proposal}

Provide:
1. RISK_LEVEL: [LOW / MEDIUM / HIGH / CRITICAL]
2. KEY_RISKS: [List specific risks]
3. MITIGATION: [How to reduce risks]
4. RECOMMENDATION: [Proceed with caution / Modify / Reject]
"""
        response = await self.think(prompt)
        self.add_thought(f"Assessed risk for: {proposal.get('title', 'Unknown')}")

        return {
            "action": "assess_risk",
            "assessment": response,
        }
