import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.domain import Project
from app.services.store import store
from app.workflow.orchestrator import orchestrator


@pytest.fixture(autouse=True)
def reset_store():
    store._projects.clear()
    store._subscribers.clear()


@pytest.mark.asyncio
async def test_intake_to_script_approval_to_delivery():
    project = Project(
        owner_id="usr_ada",
        title="The Kitchen Table Archive",
        raw_story="Before anyone wrote it down, the family story lived in the steam above a Sunday pot. "
        "A grandchild found the stained card years later and read it aloud.",
    )
    await store.save(project)
    project = await orchestrator.start_project(project)
    assert project.artifact("brief") is not None
    assert project.artifact("script") is not None
    assert project.status.value == "awaiting_approval"

    project = await orchestrator.approve_script(project, actor="usr_ada")
    assert project.gates["script_approval"] is True
    assert project.gates["rights_clearance"] is True
    assert project.artifact("master") is not None
    assert project.status.value == "delivered"


@pytest.mark.asyncio
async def test_rights_block_on_lyrics():
    project = Project(
        owner_id="usr_ada",
        title="Cover Night",
        raw_story="We sang the copyrighted lyrics of a famous single word for word until dawn.",
    )
    await store.save(project)
    project = await orchestrator.start_project(project)
    assert project.status.value == "blocked"
    assert any(event.type == "rights.blocked" for event in project.events)


@pytest.mark.asyncio
async def test_api_demo_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        auth = await client.post("/api/auth/demo", json={"name": "Ada"})
        assert auth.status_code == 200
        token = auth.json()["access_token"]
        created = await client.post(
            "/api/projects",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Letters Home",
                "story": "A box of unsent letters sat in the attic until a rainy Thursday in March.",
            },
        )
        assert created.status_code == 200
        project_id = created.json()["id"]
        approved = await client.post(
            f"/api/projects/{project_id}/approve-script",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert approved.status_code == 200
        assert approved.json()["status"] == "delivered"
