"""Engineering Expert agent."""

from typing import Any

from ..base import BaseAgent


ENGINEERING_SYSTEM_PROMPT = """You are an Engineering Expert in a virtual company.
Your role is to design, estimate, and guide technical implementation.

Responsibilities:
- Design technical architecture and systems
- Estimate effort and identify risks
- Define implementation approaches
- Ensure technical quality and best practices
- Balance speed with maintainability

When working on engineering:
1. Consider scalability, security, and reliability
2. Choose pragmatic solutions over perfect ones
3. Identify and communicate trade-offs clearly
4. Anticipate technical debt and mitigation
5. Think about operational concerns (monitoring, deployment)

Be practical, thorough, and solution-oriented."""


class EngineeringExpert(BaseAgent):
    """Engineering expert agent."""

    def __init__(self, llm_client=None, name: str = "Engineering Expert"):
        super().__init__(
            role="Engineering",
            name=name,
            llm_client=llm_client,
            system_prompt=ENGINEERING_SYSTEM_PROMPT,
        )

    async def act(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute an engineering task."""
        action = task.get("action")

        if action == "design_architecture":
            return await self._design_architecture(task)
        elif action == "estimate_effort":
            return await self._estimate_effort(task)
        elif action == "technical_review":
            return await self._technical_review(task)
        elif action == "implementation_plan":
            return await self._implementation_plan(task)
        else:
            return {"error": f"Unknown action: {action}"}

    async def _design_architecture(self, task: dict[str, Any]) -> dict[str, Any]:
        """Design technical architecture."""
        requirements = task.get("requirements", {})
        constraints = task.get("constraints", {})

        prompt = f"""Design technical architecture for:

Requirements: {requirements}
Constraints: {constraints}

Provide:
1. HIGH_LEVEL_DESIGN: [System components and interactions]
2. TECH_STACK: [Recommended technologies with rationale]
3. DATA_MODEL: [Key entities and relationships]
4. API_DESIGN: [Key interfaces]
5. SECURITY_CONSIDERATIONS: [Authentication, authorization, data protection]
6. SCALABILITY_APPROACH: [How to handle growth]
7. TRADE_OFFS: [Key decisions and alternatives considered]
"""
        response = await self.think(prompt)
        self.add_thought("Designed architecture")

        return {
            "action": "design_architecture",
            "design": response,
        }

    async def _estimate_effort(self, task: dict[str, Any]) -> dict[str, Any]:
        """Estimate development effort."""
        scope = task.get("scope", {})
        team_capacity = task.get("team_capacity", {})

        prompt = f"""Estimate effort for:

Scope: {scope}
Team capacity: {team_capacity}

Provide:
1. BREAKDOWN: [Tasks/subtasks with individual estimates]
2. TOTAL_EFFORT: [In person-days or story points]
3. TIMELINE: [Calendar time with parallelization]
4. UNCERTAINTY: [Confidence level and risk factors]
5. ASSUMPTIONS: [What the estimate assumes]
6. BUFFER: [Recommended contingency]
"""
        response = await self.think(prompt)
        self.add_thought("Estimated effort")

        return {
            "action": "estimate_effort",
            "estimate": response,
        }

    async def _technical_review(self, task: dict[str, Any]) -> dict[str, Any]:
        """Review technical approach or code."""
        artifact = task.get("artifact", "")
        review_type = task.get("review_type", "design")

        prompt = f"""Review the following {review_type}:

{artifact}

Provide:
1. STRENGTHS: [What's done well]
2. CONCERNS: [Issues or risks]
3. SUGGESTIONS: [Specific improvements]
4. QUESTIONS: [What needs clarification]
5. APPROVAL_STATUS: [APPROVE / APPROVE_WITH_CHANGES / REQUEST_CHANGES]
6. PRIORITY_FIXES: [Must-fix issues if any]
"""
        response = await self.think(prompt)
        self.add_thought(f"Reviewed {review_type}")

        return {
            "action": "technical_review",
            "review_type": review_type,
            "review": response,
        }

    async def _implementation_plan(self, task: dict[str, Any]) -> dict[str, Any]:
        """Create detailed implementation plan."""
        feature = task.get("feature", "")
        architecture = task.get("architecture", {})

        prompt = f"""Create implementation plan for: {feature}

Architecture: {architecture}

Provide:
1. MILESTONES: [Key deliverables with dates]
2. TASKS: [Detailed task breakdown]
3. DEPENDENCIES: [What must be done first]
4. RISKS: [What could go wrong]
5. MITIGATION: [How to handle risks]
6. DEFINITION_OF_DONE: [When is it complete]
7. TESTING_STRATEGY: [How to verify quality]
"""
        response = await self.think(prompt)
        self.add_thought(f"Created implementation plan for: {feature}")

        return {
            "action": "implementation_plan",
            "feature": feature,
            "plan": response,
        }
