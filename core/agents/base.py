"""Base agent class for DeamCompan."""

import uuid
from abc import ABC, abstractmethod
from typing import Any

from core.artifacts.models import AgentThought
from core.llm.base import LLMClient, LLMMessage


class BaseAgent(ABC):
    """Base class for all agents in DeamCompan."""

    def __init__(
        self,
        role: str,
        name: str | None = None,
        llm_client: LLMClient | None = None,
        system_prompt: str = "",
    ):
        self.id = str(uuid.uuid4())[:8]
        self.role = role
        self.name = name or f"{role}_{self.id}"
        self.llm_client = llm_client
        self.system_prompt = system_prompt
        self.context: dict[str, Any] = {}
        self.thoughts: list[AgentThought] = []

    def set_context(self, key: str, value: Any) -> None:
        """Set context information for the agent."""
        self.context[key] = value

    def get_context(self, key: str) -> Any | None:
        """Get context information."""
        return self.context.get(key)

    def add_thought(self, content: str, meeting_id: str | None = None) -> AgentThought:
        """Record a thought/contribution from this agent."""
        thought = AgentThought(
            agent_id=self.id,
            agent_role=self.role,
            content=content,
            meeting_id=meeting_id,
        )
        self.thoughts.append(thought)
        return thought

    async def think(
        self,
        prompt: str,
        temperature: float = 0.7,
    ) -> str:
        """Use LLM to generate a thought/response."""
        if not self.llm_client:
            raise ValueError(f"Agent {self.name} has no LLM client configured")

        messages = []
        if self.system_prompt:
            messages.append(LLMMessage("system", self.system_prompt))

        # Add context as system message if available
        if self.context:
            context_str = "Context:\n" + "\n".join(
                f"- {k}: {v}" for k, v in self.context.items()
            )
            messages.append(LLMMessage("system", context_str))

        messages.append(LLMMessage("user", prompt))

        response = await self.llm_client.complete(messages, temperature=temperature)
        return response.content

    @abstractmethod
    async def act(self, task: dict[str, Any]) -> dict[str, Any]:
        """Perform an action based on a task. Must be implemented by subclasses."""
        pass

    def to_dict(self) -> dict[str, Any]:
        """Serialize agent state."""
        return {
            "id": self.id,
            "role": self.role,
            "name": self.name,
            "context": self.context,
        }
