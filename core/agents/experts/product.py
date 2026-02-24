"""Product Expert agent."""

from typing import Any

from core.agents.base import BaseAgent


PRODUCT_SYSTEM_PROMPT = """You are a Product Expert in a virtual company.
Your role is to define, prioritize, and guide product development.

Responsibilities:
- Define product vision, strategy, and roadmap
- Prioritize features based on value and effort
- Write product requirements and specifications
- Analyze user needs and market fit
- Coordinate with engineering on implementation

When working on product:
1. Focus on user problems, not just features
2. Use data to inform prioritization
3. Balance short-term wins with long-term vision
4. Clearly articulate requirements
5. Anticipate edge cases and dependencies

Be user-centric, analytical, and pragmatic."""


class ProductExpert(BaseAgent):
    """Product expert agent."""

    def __init__(self, llm_client=None, name: str = "Product Expert"):
        super().__init__(
            role="Product",
            name=name,
            llm_client=llm_client,
            system_prompt=PRODUCT_SYSTEM_PROMPT,
        )

    async def act(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute a product task."""
        action = task.get("action")

        if action == "define_vision":
            return await self._define_vision(task)
        elif action == "prioritize_features":
            return await self._prioritize_features(task)
        elif action == "write_prd":
            return await self._write_prd(task)
        elif action == "user_research":
            return await self._user_research(task)
        else:
            return {"error": f"Unknown action: {action}"}

    async def _define_vision(self, task: dict[str, Any]) -> dict[str, Any]:
        """Define product vision and strategy."""
        context = task.get("context", {})
        market = task.get("market", "")

        prompt = f"""Define product vision and strategy:

Market: {market}
Context: {context}

Provide:
1. VISION_STATEMENT: [Inspiring, clear vision]
2. TARGET_USERS: [Who we serve]
3. KEY_PROBLEMS: [Problems we solve]
4. UNIQUE_VALUE: [Why choose us]
5. SUCCESS_METRICS: [How we measure success]
6. STRATEGIC_PILLARS: [3-5 core strategic areas]
"""
        response = await self.think(prompt)
        self.add_thought("Defined product vision")

        return {
            "action": "define_vision",
            "vision": response,
        }

    async def _prioritize_features(self, task: dict[str, Any]) -> dict[str, Any]:
        """Prioritize features for development."""
        features = task.get("features", [])
        strategy = task.get("strategy", "")
        constraints = task.get("constraints", {})

        prompt = f"""Prioritize the following features:

Strategy: {strategy}
Constraints: {constraints}
Features: {features}

Provide:
1. PRIORITIZED_LIST: [Ranked by RICE or similar framework]
2. RATIONALE: [Why each priority level]
3. QUICK_WINS: [High value, low effort]
4. MAJOR_BETS: [High value, high effort]
5. DEPRECATE: [Low value features to remove]
6. ROADMAP: [Suggested sequence over quarters]
"""
        response = await self.think(prompt)
        self.add_thought("Prioritized features")

        return {
            "action": "prioritize_features",
            "priorities": response,
        }

    async def _write_prd(self, task: dict[str, Any]) -> dict[str, Any]:
        """Write a Product Requirements Document."""
        feature = task.get("feature", "")
        context = task.get("context", {})

        prompt = f"""Write a PRD for: {feature}

Context: {context}

Include:
1. OVERVIEW: [What and why]
2. OBJECTIVES: [What success looks like]
3. USER_STORIES: [As a [user], I want [goal], so that [benefit]]
4. ACCEPTANCE_CRITERIA: [Specific, testable criteria]
5. FUNCTIONAL_REQUIREMENTS: [What the feature does]
6. NON_FUNCTIONAL_REQUIREMENTS: [Performance, security, etc.]
7. OPEN_QUESTIONS: [What needs clarification]
8. SUCCESS_METRICS: [How to measure impact]
"""
        response = await self.think(prompt)
        self.add_thought(f"Wrote PRD for: {feature}")

        return {
            "action": "write_prd",
            "feature": feature,
            "prd": response,
        }

    async def _user_research(self, task: dict[str, Any]) -> dict[str, Any]:
        """Analyze user needs and feedback."""
        feedback = task.get("feedback", [])
        user_segments = task.get("user_segments", [])

        prompt = f"""Analyze user research:

User segments: {user_segments}
Feedback/data: {feedback}

Provide:
1. KEY_INSIGHTS: [Most important findings]
2. PAIN_POINTS: [Major user frustrations]
3. DELIGHTERS: [What users love]
4. UNMET_NEEDS: [Opportunities]
5. SEGMENT_DIFFERENCES: [How needs vary by segment]
6. PRODUCT_IMPLICATIONS: [What to build/change]
"""
        response = await self.think(prompt)
        self.add_thought("Analyzed user research")

        return {
            "action": "user_research",
            "insights": response,
        }
