from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.models.domain import Artifact, Event, Project, new_id
from app.services.llm import LLMAdapter, get_llm


@dataclass
class AgentResult:
    events: list[Event] = field(default_factory=list)
    artifacts: list[Artifact] = field(default_factory=list)
    status: str | None = None
    gate_updates: dict[str, bool] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)


class BaseAgent:
    name = "base"
    purpose = ""

    def __init__(self, llm: LLMAdapter | None = None) -> None:
        self.llm = llm or get_llm()

    async def perceive(self, project: Project, trigger: Event) -> dict[str, Any]:
        return {
            "project_id": project.id,
            "status": project.status.value,
            "trigger": trigger.type,
            "story": project.raw_story[:4000],
            "style": project.style_preferences,
        }

    async def reason(self, perception: dict[str, Any]) -> str:
        return f"{self.name} considering {perception['trigger']} for {perception['project_id']}"

    async def plan(self, perception: dict[str, Any], reasoning: str) -> list[str]:
        return ["act"]

    async def evaluate(self, options: list[str]) -> str:
        return options[0]

    async def act(self, project: Project, trigger: Event, perception: dict[str, Any]) -> AgentResult:
        raise NotImplementedError

    async def verify(self, project: Project, result: AgentResult) -> bool:
        return True

    async def learn(self, project: Project, result: AgentResult) -> None:
        return None

    def event(self, project: Project, type_: str, summary: str, payload: dict | None = None) -> Event:
        return Event(
            id=new_id("evt"),
            project_id=project.id,
            type=type_,
            actor=self.name,
            summary=summary,
            payload=payload or {},
        )

    async def run(self, project: Project, trigger: Event) -> AgentResult:
        perception = await self.perceive(project, trigger)
        await self.reason(perception)
        options = await self.plan(perception, "")
        await self.evaluate(options)
        result = await self.act(project, trigger, perception)
        ok = await self.verify(project, result)
        if not ok:
            result.events.append(
                self.event(project, "agent.failed", f"{self.name} failed verification")
            )
        await self.learn(project, result)
        return result
