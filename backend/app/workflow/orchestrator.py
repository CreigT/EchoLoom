from __future__ import annotations

import asyncio

from app.agents.roster import AGENT_REGISTRY
from app.models.domain import Event, Project, ProjectStatus
from app.services.store import store


class Orchestrator:
    """Event-driven workflow engine.

    Routing is explicit so rights and payment can never be skipped by a creative agent.
    """

    def __init__(self) -> None:
        self._apply_lock = asyncio.Lock()

    async def start_project(self, project: Project) -> Project:
        kick = Event(
            project_id=project.id,
            type="project.submitted",
            actor="system",
            summary="Customer submitted a story",
        )
        await store.append_event(project, kick)
        await self._run_agents(project, kick, ["security", "intake"])
        project = await store.get(project.id) or project
        if project.status == ProjectStatus.BLOCKED:
            await self._run_agents(project, kick, ["ceo"])
            return project
        latest = project.events[-1]
        await self._run_agents(project, latest, ["architect", "rights", "monetization"])
        return await store.get(project.id) or project

    async def approve_script(self, project: Project, actor: str) -> Project:
        project.gates["script_approval"] = True
        project.status = ProjectStatus.PRODUCING
        approval = Event(
            project_id=project.id,
            type="customer.script_approved",
            actor=actor,
            summary="Customer approved the narration script",
        )
        await store.append_event(project, approval)
        await self._run_agents(project, approval, ["voice", "sound"])
        project = await store.get(project.id) or project
        await self._run_agents(project, approval, ["rights"])
        project = await store.get(project.id) or project
        if project.status == ProjectStatus.BLOCKED:
            await self._run_agents(project, approval, ["ceo"])
            return project
        await self._run_agents(project, approval, ["production"])
        project = await store.get(project.id) or project
        if project.artifact("master"):
            await self._run_agents(project, approval, ["marketplace", "finance", "success", "analytics", "ceo"])
        return await store.get(project.id) or project

    async def _run_agents(self, project: Project, trigger: Event, names: list[str]) -> None:
        async def run_one(name: str) -> None:
            snapshot = await store.get(project.id) or project
            result = await AGENT_REGISTRY[name].run(snapshot, trigger)
            async with self._apply_lock:
                current = await store.get(project.id) or snapshot
                if result.status:
                    incoming = ProjectStatus(result.status)
                    if current.status != ProjectStatus.BLOCKED or incoming == ProjectStatus.BLOCKED:
                        current.status = incoming
                current.gates.update(result.gate_updates)
                for artifact in result.artifacts:
                    current.add_artifact(artifact)
                await store.save(current)
                for event in result.events:
                    await store.append_event(current, event)

        await asyncio.gather(*(run_one(name) for name in names))


orchestrator = Orchestrator()
