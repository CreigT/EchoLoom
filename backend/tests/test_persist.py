from pathlib import Path

import pytest

from app.models.domain import Project
from app.services.store import ProjectStore


@pytest.mark.asyncio
async def test_projects_survive_reload(tmp_path: Path):
    path = tmp_path / "projects.json"
    first = ProjectStore(persist_path=path)
    project = Project(owner_id="usr_ada", title="Letters", raw_story="A box of unsent letters sat in the attic for years.")
    await first.save(project)

    second = ProjectStore(persist_path=path)
    loaded = await second.get(project.id)
    assert loaded is not None
    assert loaded.title == "Letters"
