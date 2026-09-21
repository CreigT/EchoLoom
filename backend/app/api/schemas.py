from pydantic import BaseModel, Field


class DemoAuthRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str


class ProjectCreate(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    story: str = Field(min_length=20, max_length=20000)
    style_preferences: str = "warm memoir, cinematic pacing"
    package_type: str = "audiobook"
    visibility: str = "private"
    voice_consent: bool = False


class ArtifactOut(BaseModel):
    id: str
    kind: str
    title: str
    content: str
    metadata: dict


class EventOut(BaseModel):
    id: str
    type: str
    actor: str
    summary: str
    payload: dict
    created_at: str


class ProjectOut(BaseModel):
    id: str
    title: str
    status: str
    risk_score: int
    risk_flags: list[dict]
    gates: dict
    package_type: str
    visibility: str
    voice_consent: bool
    style_preferences: str
    raw_story: str
    artifacts: list[ArtifactOut]
    events: list[EventOut]
    created_at: str
    updated_at: str
