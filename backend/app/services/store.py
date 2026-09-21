from __future__ import annotations

import asyncio
from typing import Iterable

from app.models.domain import Event, Project


class ProjectStore:
    def __init__(self) -> None:
        self._projects: dict[str, Project] = {}
        self._lock = asyncio.Lock()
        self._subscribers: dict[str, list[asyncio.Queue]] = {}

    async def save(self, project: Project) -> Project:
        async with self._lock:
            self._projects[project.id] = project
        return project

    async def get(self, project_id: str) -> Project | None:
        return self._projects.get(project_id)

    async def for_owner(self, owner_id: str) -> list[Project]:
        return [p for p in self._projects.values() if p.owner_id == owner_id]

    async def all(self) -> list[Project]:
        return list(self._projects.values())

    async def append_event(self, project: Project, event: Event) -> Event:
        project.add_event(event)
        await self.save(project)
        await self.publish(project.id, event)
        return event

    def subscribe(self, project_id: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.setdefault(project_id, []).append(queue)
        return queue

    def unsubscribe(self, project_id: str, queue: asyncio.Queue) -> None:
        listeners = self._subscribers.get(project_id, [])
        if queue in listeners:
            listeners.remove(queue)

    async def publish(self, project_id: str, event: Event) -> None:
        for queue in list(self._subscribers.get(project_id, [])):
            await queue.put(event)

    def seeded(self) -> Iterable[Project]:
        return self._projects.values()


store = ProjectStore()
