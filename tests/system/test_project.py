
import pytest

from ansible_events_ui.project import build_project

@pytest.mark.asyncio
async def test_build():

    project = await build_project()
    assert project is not None
