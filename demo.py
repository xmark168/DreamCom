"""Demo script for DeamCompan.

This script demonstrates the core functionality of DeamCompan:
1. Create agents (BOD, CEO, Strategy, Product, Engineering)
2. Set up a workspace
3. Run a strategic planning meeting
4. Show the results
"""

import asyncio
import os
from datetime import datetime

from deamcompan.core.agents.bod import BoardOfDirectors
from deamcompan.core.agents.ceo import CEOOrchestrator
from deamcompan.core.agents.experts.engineering import EngineeringExpert
from deamcompan.core.agents.experts.product import ProductExpert
from deamcompan.core.agents.experts.strategy import StrategyExpert
from deamcompan.core.artifacts.models import Initiative
from deamcompan.core.artifacts.registry import DecisionRegistry
from deamcompan.core.artifacts.store import ArtifactStore
from deamcompan.core.llm.factory import LLMClientFactory
from deamcompan.core.meetings.engine import MeetingEngine
from deamcompan.core.meetings.types import MeetingType
from deamcompan.core.workspace.state import WorkspaceState


async def main():
    """Run the DeamCompan demo."""
    print("=" * 60)
    print("DeamCompan Demo - Virtual Company Workspace")
    print("=" * 60)
    print()

    # Check for API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: No API keys found!")
        print("Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable.")
        print("Demo will run in 'mock mode' without actual LLM calls.")
        print()
        use_mock = True
    else:
        use_mock = False

    # Initialize storage
    print("📁 Initializing workspace...")
    store = ArtifactStore("./demo_workspace")
    workspace = WorkspaceState(store)
    registry = DecisionRegistry(store)
    meeting_engine = MeetingEngine(store)
    print("✅ Workspace initialized")
    print()

    # Create agents
    print("🤖 Creating agents...")

    if use_mock:
        # Create agents without LLM for demo
        bod = BoardOfDirectors(None, "Board of Directors")
        ceo = CEOOrchestrator(None, "CEO")
        strategy = StrategyExpert(None, "Strategy Expert")
        product = ProductExpert(None, "Product Expert")
        engineering = EngineeringExpert(None, "Engineering Expert")
    else:
        # Create agents with LLM
        provider = "openai" if os.getenv("OPENAI_API_KEY") else "anthropic"
        llm_client = LLMClientFactory.create(provider)

        bod = BoardOfDirectors(llm_client, "Board of Directors")
        ceo = CEOOrchestrator(llm_client, "CEO")
        strategy = StrategyExpert(llm_client, "Strategy Expert")
        product = ProductExpert(llm_client, "Product Expert")
        engineering = EngineeringExpert(llm_client, "Engineering Expert")

    # Register agents in workspace
    workspace.register_agent(bod)
    workspace.register_agent(ceo)
    workspace.register_agent(strategy)
    workspace.register_agent(product)
    workspace.register_agent(engineering)

    print(f"  - {bod.name} ({bod.role})")
    print(f"  - {ceo.name} ({ceo.role})")
    print(f"  - {strategy.name} ({strategy.role})")
    print(f"  - {product.name} ({product.role})")
    print(f"  - {engineering.name} ({engineering.role})")
    print("✅ Agents created")
    print()

    # Create an initiative
    print("🎯 Creating initiative...")
    initiative = Initiative(
        id="init-001",
        name="AI Product Strategy 2025",
        description="Define the AI product strategy for the upcoming year",
        owner="Strategy",
    )
    workspace.add_initiative(initiative)
    print(f"  - {initiative.name}")
    print("✅ Initiative created")
    print()

    # Run a strategic planning meeting
    print("📅 Running Strategic Planning Meeting...")
    print("-" * 60)

    meeting = await meeting_engine.create_meeting(
        title="Q1 Strategic Planning",
        meeting_type=MeetingType.EXECUTIVE_REVIEW,
        agenda=[
            "Review current market position",
            "Discuss AI product opportunities",
            "Prioritize initiatives for Q1",
            "Assign action items",
        ],
        participants=[ceo, strategy, product, engineering],
    )

    print(f"Meeting ID: {meeting.meeting_id}")
    print(f"Title: {meeting.title}")
    print(f"Participants: {', '.join(p.name for p in meeting.participants)}")
    print()

    if use_mock:
        print("📝 Mock mode - simulating meeting without LLM calls")
        print()
        print("Phase 1: Async Preparation")
        print("  - Each expert prepares their input...")
        print("  - Strategy: Market analysis complete")
        print("  - Product: Feature priorities identified")
        print("  - Engineering: Technical feasibility assessed")
        print()
        print("Phase 2: Synchronous Decision")
        print("  - Round 1: Initial perspectives shared")
        print("  - Round 2: Convergence on key decisions")
        print()
        print("Decisions made:")
        print("  1. DECISION: Focus on AI-powered analytics product")
        print("  2. DECISION: Launch MVP by end of Q1")
        print()
        print("Action items:")
        print("  - ACTION: Conduct user research | OWNER: Product | DEADLINE: 2 weeks")
        print("  - ACTION: Design technical architecture | OWNER: Engineering | DEADLINE: 3 weeks")
        print()
    else:
        # Run actual meeting with LLM
        print("Running meeting with LLM (this may take a minute)...")
        result = await meeting_engine.run_meeting(meeting.meeting_id)

        print("Phase 1: Async Preparation Complete")
        print()
        print("Phase 2: Synchronous Decision Complete")
        print()

        if "decision_results" in result:
            decisions = result["decision_results"].get("decisions", [])
            actions = result["decision_results"].get("action_items", [])

            print(f"Decisions made: {len(decisions)}")
            for d in decisions:
                print(f"  - {d['description'][:80]}...")

            print()
            print(f"Action items: {len(actions)}")
            for a in actions:
                print(f"  - {a['description'][:60]}... (Owner: {a['owner']})")

    print("-" * 60)
    print("✅ Meeting completed")
    print()

    # Show workspace metrics
    print("📊 Workspace Metrics")
    print("-" * 60)
    metrics = workspace.get_metrics()
    print(f"Agents: {metrics['agents']}")
    print(f"Active Initiatives: {metrics['active_initiatives']}")
    print(f"Total Meetings: {metrics['total_meetings']}")
    print(f"Pending Decisions: {metrics['pending_decisions']}")
    print(f"Open Action Items: {metrics['open_action_items']}")
    print("-" * 60)
    print()

    # Show decision registry
    print("📋 Decision Registry")
    print("-" * 60)
    decisions = registry.list_all()
    if decisions:
        for d in decisions[:5]:
            status_icon = "✅" if d.status == "approved" else "⏳" if d.status == "pending" else "📝"
            print(f"{status_icon} [{d.status.upper()}] {d.title}")
    else:
        print("No decisions recorded yet.")
    print("-" * 60)
    print()

    print("=" * 60)
    print("Demo completed!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Start the API server: uvicorn deamcompan.api.main:app --reload")
    print("  2. Open the UI: http://localhost:8000")
    print("  3. Create more agents and run meetings")
    print()


if __name__ == "__main__":
    asyncio.run(main())
