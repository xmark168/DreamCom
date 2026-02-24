"""API routes for agents."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.agents.bod import BoardOfDirectors
from core.agents.ceo import CEOOrchestrator
from core.agents.experts.engineering import EngineeringExpert
from core.agents.experts.product import ProductExpert
from core.agents.experts.strategy import StrategyExpert
from core.llm.factory import LLMClientFactory
from api.main import workspace

router = APIRouter()

# In-memory agent registry for the API
_agent_registry: dict[str, any] = {}


class AgentCreateRequest(BaseModel):
    role: str
    name: str | None = None
    provider: str = "openai"
    model: str | None = None


class AgentResponse(BaseModel):
    id: str
    role: str
    name: str


@router.post("/create", response_model=AgentResponse)
async def create_agent(request: AgentCreateRequest):
    """Create a new agent."""
    try:
        llm_client = LLMClientFactory.create(request.provider, request.model)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if request.role == "BOD":
        agent = BoardOfDirectors(llm_client, request.name or "Board of Directors")
    elif request.role == "CEO":
        agent = CEOOrchestrator(llm_client, request.name or "CEO")
    elif request.role == "Strategy":
        agent = StrategyExpert(llm_client, request.name or "Strategy Expert")
    elif request.role == "Product":
        agent = ProductExpert(llm_client, request.name or "Product Expert")
    elif request.role == "Engineering":
        agent = EngineeringExpert(llm_client, request.name or "Engineering Expert")
    else:
        raise HTTPException(status_code=400, detail=f"Unknown role: {request.role}")

    _agent_registry[agent.id] = agent
    if workspace:
        workspace.register_agent(agent)

    return AgentResponse(id=agent.id, role=agent.role, name=agent.name)


@router.get("/list")
async def list_agents():
    """List all registered agents."""
    return [
        {"id": a.id, "role": a.role, "name": a.name}
        for a in _agent_registry.values()
    ]


@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent details."""
    agent = _agent_registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return {
        "id": agent.id,
        "role": agent.role,
        "name": agent.name,
        "context": agent.context,
        "thoughts": [
            {"content": t.content, "timestamp": t.timestamp.isoformat()}
            for t in agent.thoughts[-10:]  # Last 10 thoughts
        ],
    }


@router.post("/{agent_id}/act")
async def agent_act(agent_id: str, task: dict):
    """Have an agent perform a task."""
    agent = _agent_registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    try:
        result = await agent.act(task)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
