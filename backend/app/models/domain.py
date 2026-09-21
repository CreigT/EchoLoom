from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class ProjectStatus(str, Enum):
    INTAKE = "intake"
    BRIEFING = "briefing"
    SCRIPTING = "scripting"
    AWAITING_APPROVAL = "awaiting_approval"
    PRODUCING = "producing"
    CLEARING = "clearing"
    MASTERING = "mastering"
    PUBLISHING = "publishing"
    DELIVERED = "delivered"
    BLOCKED = "blocked"
    CLOSED = "closed"
    REJECTED = "rejected"


class RiskFlag(BaseModel):
    code: str
    severity: str
    detail: str


class Artifact(BaseModel):
    id: str = Field(default_factory=lambda: new_id("art"))
    kind: str
    title: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)


class Event(BaseModel):
    id: str = Field(default_factory=lambda: new_id("evt"))
    project_id: str
    type: str
    actor: str
    summary: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)


class Project(BaseModel):
    id: str = Field(default_factory=lambda: new_id("prj"))
    owner_id: str
    title: str
    raw_story: str
    style_preferences: str = "warm memoir, cinematic pacing"
    status: ProjectStatus = ProjectStatus.INTAKE
    risk_score: int = 0
    risk_flags: list[RiskFlag] = Field(default_factory=list)
    artifacts: list[Artifact] = Field(default_factory=list)
    events: list[Event] = Field(default_factory=list)
    gates: dict[str, bool] = Field(
        default_factory=lambda: {
            "script_approval": False,
            "rights_clearance": False,
            "payment": False,
        }
    )
    package_type: str = "audiobook"
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    def add_event(self, event: Event) -> Event:
        self.events.append(event)
        self.updated_at = utcnow()
        return event

    def add_artifact(self, artifact: Artifact) -> Artifact:
        self.artifacts.append(artifact)
        self.updated_at = utcnow()
        return artifact

    def artifact(self, kind: str) -> Artifact | None:
        for item in reversed(self.artifacts):
            if item.kind == kind:
                return item
        return None
