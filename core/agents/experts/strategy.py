"""Strategy Expert agent."""

from typing import Any

from core.agents.base import BaseAgent


STRATEGY_SYSTEM_PROMPT = """You are a Strategy Expert in a virtual company.
Your role is to analyze markets, competitors, and opportunities to inform strategic decisions.

Responsibilities:
- Analyze market trends and competitive landscape
- Identify growth opportunities and threats
- Develop strategic frameworks and options
- Support long-term planning and scenario analysis
- Provide data-driven strategic recommendations

When analyzing:
1. Consider multiple perspectives and scenarios
2. Use structured frameworks (SWOT, Porter's, etc.)
3. Quantify impacts where possible
4. Highlight key uncertainties and assumptions
5. Provide actionable recommendations

Be thorough, analytical, and forward-looking."""


class StrategyExpert(BaseAgent):
    """Strategy expert agent."""

    def __init__(self, llm_client=None, name: str = "Strategy Expert"):
        super().__init__(
            role="Strategy",
            name=name,
            llm_client=llm_client,
            system_prompt=STRATEGY_SYSTEM_PROMPT,
        )

    async def act(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute a strategy task."""
        action = task.get("action")

        if action == "market_analysis":
            return await self._market_analysis(task)
        elif action == "competitive_analysis":
            return await self._competitive_analysis(task)
        elif action == "scenario_planning":
            return await self._scenario_planning(task)
        elif action == "strategic_options":
            return await self._strategic_options(task)
        else:
            return {"error": f"Unknown action: {action}"}

    async def _market_analysis(self, task: dict[str, Any]) -> dict[str, Any]:
        """Analyze market trends and opportunities."""
        market = task.get("market", "")
        context = task.get("context", {})

        prompt = f"""Analyze the following market:

Market: {market}
Context: {context}

Provide:
1. MARKET_SIZE: [TAM, SAM, SOM if available]
2. GROWTH_TRENDS: [Key trends and drivers]
3. CUSTOMER_SEGMENTS: [Important segments]
4. OPPORTUNITIES: [Where to focus]
5. THREATS: [Risks to monitor]
6. RECOMMENDATIONS: [Strategic implications]
"""
        response = await self.think(prompt)
        self.add_thought(f"Analyzed market: {market}")

        return {
            "action": "market_analysis",
            "market": market,
            "analysis": response,
        }

    async def _competitive_analysis(self, task: dict[str, Any]) -> dict[str, Any]:
        """Analyze competitive landscape."""
        competitors = task.get("competitors", [])
        our_position = task.get("our_position", {})

        prompt = f"""Analyze the competitive landscape:

Our position: {our_position}
Key competitors: {competitors}

Provide:
1. COMPETITOR_MAP: [Positioning of each competitor]
2. OUR_ADVANTAGES: [What we do better]
3. OUR_GAPS: [Where we lag]
4. DIFFERENTIATION: [How to stand out]
5. COMPETITIVE_THREATS: [Moves to watch]
6. STRATEGIC_RESPONSE: [How to compete effectively]
"""
        response = await self.think(prompt)
        self.add_thought("Analyzed competitive landscape")

        return {
            "action": "competitive_analysis",
            "analysis": response,
        }

    async def _scenario_planning(self, task: dict[str, Any]) -> dict[str, Any]:
        """Develop scenario plans."""
        topic = task.get("topic", "")
        time_horizon = task.get("time_horizon", "3 years")

        prompt = f"""Develop scenario plans for: {topic}
Time horizon: {time_horizon}

Provide:
1. BASE_CASE: [Most likely scenario]
2. BEST_CASE: [Optimistic but plausible]
3. WORST_CASE: [Pessimistic but plausible]
4. WILD_CARD: [Low probability, high impact]
5. INDICATORS: [Signals to watch for each scenario]
6. CONTINGENCY_PLANS: [How to prepare for each]
"""
        response = await self.think(prompt)
        self.add_thought(f"Developed scenarios for: {topic}")

        return {
            "action": "scenario_planning",
            "topic": topic,
            "scenarios": response,
        }

    async def _strategic_options(self, task: dict[str, Any]) -> dict[str, Any]:
        """Generate and evaluate strategic options."""
        objective = task.get("objective", "")
        constraints = task.get("constraints", {})

        prompt = f"""Develop strategic options for:

Objective: {objective}
Constraints: {constraints}

Provide:
1. OPTION_A: [Description, pros, cons, resource needs]
2. OPTION_B: [Description, pros, cons, resource needs]
3. OPTION_C: [Description, pros, cons, resource needs]
4. COMPARISON: [Side-by-side comparison]
5. RECOMMENDATION: [Best option with rationale]
6. IMPLEMENTATION: [Key steps if chosen]
"""
        response = await self.think(prompt)
        self.add_thought(f"Generated strategic options for: {objective}")

        return {
            "action": "strategic_options",
            "objective": objective,
            "options": response,
        }
