from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Iterable

from app.core.config import get_settings
from app.models.domain import Event, Project


class ProjectStore:
    def __init__(self, persist_path: Path | None = None) -> None:
        self._projects: dict[str, Project] = {}
        self._lock = asyncio.Lock()
        self._subscribers: dict[str, list[asyncio.Queue]] = {}
        settings = get_settings()
        self._persist_path = persist_path
        if persist_path is None and settings.persist_enabled:
            self._persist_path = settings.data_path() / "projects.json"
        self._loaded = False

    async def load(self) -> None:
        if self._loaded or not self._persist_path or not self._persist_path.exists():
            self._loaded = True
            return
        raw = self._persist_path.read_text(encoding="utf-8")
        if not raw.strip():
            self._loaded = True
            return
        payload = json.loads(raw)
        for item in payload.get("projects", []):
            project = Project.model_validate(item)
            self._projects[project.id] = project
        self._loaded = True

    def _dump(self) -> None:
        if not self._persist_path:
            return
        self._persist_path.parent.mkdir(parents=True, exist_ok=True)
        body = {"projects": [p.model_dump(mode="json") for p in self._projects.values()]}
        tmp = self._persist_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(body, indent=2), encoding="utf-8")
        tmp.replace(self._persist_path)

    async def save(self, project: Project) -> Project:
        async with self._lock:
            if not self._loaded:
                await self.load()
            self._projects[project.id] = project
            self._dump()
        return project

    async def get(self, project_id: str) -> Project | None:
        if not self._loaded:
            await self.load()
        return self._projects.get(project_id)

    async def for_owner(self, owner_id: str) -> list[Project]:
        if not self._loaded:
            await self.load()
        return [p for p in self._projects.values() if p.owner_id == owner_id]

    async def all(self) -> list[Project]:
        if not self._loaded:
            await self.load()
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

    def reset_memory(self) -> None:
        self._projects.clear()
        self._subscribers.clear()
        self._loaded = True
        self._persist_path = None


store = ProjectStore()
