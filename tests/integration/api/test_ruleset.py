import asyncio
from unittest.mock import patch

import aiodocker

from eda_server import ruleset
from eda_server.config.enums import DeploymentType

activation_id = 1
large_data_id = 1
execution_environment = "fedora:36"
rulesets = ""
ruleset_sources = []
inventory = ""
extravars = ""
working_directory = "/tmp"
host = "test-eda-server"
port = 15000


class MockDocker(aiodocker.docker.Docker):
    def __init__(self, *args, **kwargs):
        pass


class MockDockerContainer(aiodocker.docker.DockerContainer):
    def __init__(self, *args, **kwargs):
        pass

    def __getitem__(self, key):
        return self


class MockProc(asyncio.subprocess.Process):
    def __init__(self, *args, **kwargs):
        self.pid = 19999


def test_resolve_activation_function():
    src = {}

    f = ruleset.resolve_activation_function(src)
    assert f is ruleset.create_websocket_docker_activation

    for _type in ("websocket", "eek", None):
        src["type"] = _type
        f = ruleset.resolve_activation_function(src)
        assert f is ruleset.create_websocket_docker_activation


@patch("eda_server.ruleset.create_async_task")
@patch("eda_server.ruleset.create_local_activation", return_value=MockProc())
async def test_activate_rulesets_local(local_activate, async_task):
    await ruleset.activate_rulesets(
        DeploymentType.LOCAL,
        activation_id,
        large_data_id,
        execution_environment,
        rulesets,
        ruleset_sources,
        inventory,
        extravars,
        working_directory,
        host,
        port,
        lambda: None,
    )
    assert local_activate.called
    assert async_task.called
    assert activation_id in ruleset.activated_rulesets
    assert isinstance(ruleset.activated_rulesets[activation_id][0], MockProc)
    del ruleset.activated_rulesets[activation_id]


@patch(
    "eda_server.ruleset.create_fallback_docker_activation",
    return_value=(MockDocker(), MockDockerContainer()),
)
@patch("eda_server.ruleset.create_async_task")
async def test_activate_rulesets_docker_fallback(async_task, docker_activate):
    await ruleset.activate_rulesets(
        DeploymentType.DOCKER,
        activation_id,
        large_data_id,
        execution_environment,
        rulesets,
        ruleset_sources,
        inventory,
        extravars,
        working_directory,
        host,
        port,
        lambda: None,
    )
    assert activation_id in ruleset.activated_rulesets
    assert isinstance(
        ruleset.activated_rulesets[activation_id][0], MockDockerContainer
    )
    assert docker_activate.called
    assert async_task.called
    del ruleset.activated_rulesets[activation_id]


@patch(
    "eda_server.ruleset.create_websocket_docker_activation",
    return_value=(MockDocker(), MockDockerContainer()),
)
@patch("eda_server.ruleset.create_async_task")
async def test_activate_rulesets_docker_websocket(async_task, docker_activate):
    await ruleset.activate_rulesets(
        DeploymentType.DOCKER,
        activation_id,
        large_data_id,
        execution_environment,
        rulesets,
        [{"type": "websocket", "config": {"port": 10000}}],
        inventory,
        extravars,
        working_directory,
        host,
        port,
        lambda: None,
    )
    assert activation_id in ruleset.activated_rulesets
    assert isinstance(
        ruleset.activated_rulesets[activation_id][0], MockDockerContainer
    )
    assert docker_activate.called
    assert async_task.called
    del ruleset.activated_rulesets[activation_id]
