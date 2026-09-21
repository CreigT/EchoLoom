from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.api.deps import current_user, current_user_optional
from app.api.schemas import (
    ArtifactOut,
    DemoAuthRequest,
    EventOut,
    ProjectCreate,
    ProjectOut,
    TokenResponse,
)
from app.core.config import get_settings
from app.models.domain import Event, Project
from app.security.auth import create_token
from app.services.store import store
from app.workflow.orchestrator import orchestrator

router = APIRouter()


def _user_id(name: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in name).strip("-")
    return f"usr_{slug or 'guest'}"


def serialize(project: Project) -> ProjectOut:
    return ProjectOut(
        id=project.id,
        title=project.title,
        status=project.status.value,
        risk_score=project.risk_score,
        risk_flags=[f.model_dump() for f in project.risk_flags],
        gates=project.gates,
        package_type=project.package_type,
        visibility=project.visibility,
        voice_consent=project.voice_consent,
        style_preferences=project.style_preferences,
        raw_story=project.raw_story,
        artifacts=[
            ArtifactOut(
                id=a.id,
                kind=a.kind,
                title=a.title,
                content=a.content,
                metadata=a.metadata,
            )
            for a in project.artifacts
        ],
        events=[
            EventOut(
                id=e.id,
                type=e.type,
                actor=e.actor,
                summary=e.summary,
                payload=e.payload,
                created_at=e.created_at.isoformat(),
            )
            for e in project.events
        ],
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat(),
    )


async def _owned(project_id: str, user: dict) -> Project:
    project = await store.get(project_id)
    if not project or project.owner_id != user["sub"]:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/auth/demo", response_model=TokenResponse)
async def demo_auth(body: DemoAuthRequest) -> TokenResponse:
    user_id = _user_id(body.name)
    token = create_token(user_id)
    return TokenResponse(access_token=token, user_id=user_id, name=body.name)


@router.post("/projects", response_model=ProjectOut)
async def create_project(body: ProjectCreate, user: dict = Depends(current_user)) -> ProjectOut:
    project = Project(
        owner_id=user["sub"],
        title=body.title,
        raw_story=body.story,
        style_preferences=body.style_preferences,
        package_type=body.package_type,
        visibility=body.visibility if body.visibility in {"private", "public"} else "private",
        voice_consent=body.voice_consent,
    )
    if get_settings().require_voice_consent and not project.voice_consent:
        raise HTTPException(
            status_code=422,
            detail="Voice synthesis requires explicit consent before the swarm can produce audio.",
        )
    await store.save(project)
    project = await orchestrator.start_project(project)
    return serialize(project)


@router.get("/projects", response_model=list[ProjectOut])
async def list_projects(user: dict = Depends(current_user)) -> list[ProjectOut]:
    projects = await store.for_owner(user["sub"])
    projects.sort(key=lambda p: p.created_at, reverse=True)
    return [serialize(p) for p in projects]


@router.get("/projects/{project_id}", response_model=ProjectOut)
async def get_project(project_id: str, user: dict = Depends(current_user)) -> ProjectOut:
    return serialize(await _owned(project_id, user))


@router.post("/projects/{project_id}/approve-script", response_model=ProjectOut)
async def approve_script(project_id: str, user: dict = Depends(current_user)) -> ProjectOut:
    project = await _owned(project_id, user)
    if project.gates.get("script_approval"):
        return serialize(project)
    if not project.artifact("script"):
        raise HTTPException(status_code=409, detail="No script is ready to approve")
    project = await orchestrator.approve_script(project, actor=user["sub"])
    return serialize(project)


@router.get("/projects/{project_id}/events")
async def stream_events(
    project_id: str,
    token: str | None = Query(default=None),
    user: dict | None = Depends(current_user_optional),
) -> StreamingResponse:
    identity = user
    if identity is None and token:
        from app.security.auth import decode_token

        try:
            identity = decode_token(token)
        except ValueError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
    if identity is None:
        raise HTTPException(status_code=401, detail="Sign in to the studio first")
    project = await _owned(project_id, identity)
    queue = store.subscribe(project.id)

    async def gen():
        try:
            for event in project.events:
                yield _sse(event)
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=20)
                    yield _sse(event)
                except TimeoutError:
                    yield "event: ping\ndata: {}\n\n"
        finally:
            store.unsubscribe(project.id, queue)

    return StreamingResponse(gen(), media_type="text/event-stream")


def _sse(event: Event) -> str:
    payload = {
        "id": event.id,
        "type": event.type,
        "actor": event.actor,
        "summary": event.summary,
        "payload": event.payload,
        "created_at": event.created_at.isoformat(),
    }
    return f"event: agent\ndata: {json.dumps(payload)}\n\n"
