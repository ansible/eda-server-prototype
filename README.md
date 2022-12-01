# Event Driven Ansible Server

## Installation

For instructions on how to quickly spin up a preview instance of _eda-server_, please see [INSTALL.md](./INSTALL.md).

## Setting up a development environment

The below instructions detail how to setup a development environment for _eda-server_.

### Requirements

- [Docker](https://docs.docker.com/engine/install/) or [podman](https://podman.io/getting-started/installation)
- Docker-compose: `pip install docker-compose`
- [Taskfile](https://taskfile.dev/installation/)
  - Note: For Macs with the M1 or M2 chip make sure you download Task from the arm64 architecture (https://github.com/go-task/task/releases)
- Git
- Python >= 3.9
- python3-pip
- python3-devel
- gcc
- npm >= v16 (**NOTE:** node v17 does not seem to work with websockets)

**NOTE podman users (only for MacOS and Linux):**

- By default all dev scripts use `docker` binary. Podman users must install `podman-docker` package or run the following command:

      sudo ln -s $(which podman) $(dirname $(which podman))/docker

- `DOCKER_HOST` environment variable must be defined pointing to the podman socket to be able to use `docker-compose`. Example:

      export DOCKER_HOST=unix:///run/user/$UID/podman/podman.sock

- Ensure the `podman.socket` service is enabled and running:

      systemctl --user enable --now podman.socket

### 1. Clone the repository

First you need to clone the `eda-server` repository:

```shell
git clone https://github.com/ansible/eda-server.git
cd eda-server
```

### 2. Virtual environment

Create virtual environment and install project

```shell
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Install Ansible and `ansible.eda` collection:

```shell
pip install ansible
ansible-galaxy collection install ansible.eda
```

### 3. Set up env variables

Set up the following env variable(s) when testing/running local dev env

```shell
export EDA_DEPLOYMENT_TYPE=local
```

### 4. Services

**Note:**
Instead of running the below `task` steps individually, you can execute all tasks with `task dev:all:start` and then follow the steps in the
[Accessing the UI](#6-accessing-the-ui) section.

Start up a PostgreSQL database sever:

```shell
task dev:services:start
```

Then run database migrations:

```shell
task dev:run:migrations
```

### 5. Start api server

```shell
task dev:api:start
```

### 6. User interface

Start webpack server:

```shell
task dev:ui:start
```

### 7. Accessing the UI

1. Load a set of RBAC users and roles (config file: tools/initial_data.yml) 

Defaults from config file
```yaml
users:
  - email: 'root@example.com'
    password: 'secret'
    is_superuser: true

  - email: 'admin@example.com'
    password: 'secret'
    roles: ['admin']

  - email: 'manager@example.com'
    password: 'secret'
    roles: ['manager']

  - email: 'bob@example.com'
    password: 'secret'
```

```shell
task dev:rbac:loaddata
```

2. You can now login to the UI at <http://localhost:8080/eda/>.

API docs can be accessed at:

- <http://localhost:8080/api/docs>
- <http://localhost:8080/api/openapi.json>

**You have finished setting up the development environment.**

## Running tests

If not started, start the PostgreSQL service, which is required for running integration tests.

```shell
docker-compose -f tools/docker/docker-compose.yml up postgres
```

Run all tests:

```shell
task test
```

Or call `pytest` directly:

```shell
python -m pytest
```

## Git pre-commit hooks (optional)

To automatically run linters and code formatter you may use
[git pre-commit hooks](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks).
This project provides a configuration for [pre-commit](https://pre-commit.com/)
framework to automatically setup hooks for you.

1. First install the `pre-commit` tool:
   1. Into your virtual environment:
      ```shell
      pip install pre-commit
      ```
   
   2. Into your user directory:
      ```shell
      pip install --user pre-commit
      ```
   3. Via [pipx](https://pypa.github.io/pipx/) tool: 
      ```shell
      pipx install pre-commit
      ```

2. Then generate git pre-commit hooks:
   ```shell
   pre-commit install
   ```

You may run pre-commit manually on all tracked files by calling:
```shell
pre-commit run --all-files
```


## Logging

When you start server using the binary `eda-server`, it will use default project
logging settings. You can change the logging level by setting the environment variable
`EDA_LOG_LEVEL`. Example:

```shell
export EDA_LOG_LEVEL=debug
```

This will change log level for uvicorn and project loggers, but will not affect 3rd party libraries.

If you need to update the default project logging configuration, you should edit the
`src/eda_server/config/logging.yaml` file.

When starting server with `uvicorn` binary directly, you should specify logging configuration
file path in `--log-config` parameter. Note that in this case `--log-level` parameter only
affects `uvicorn` loggers, but not application ones. To change the application loggers levels
you should set `EDA_LOG_LEVEL` environment variable. Example:

```shell
uvicorn --log-config src/eda_server/config/logging.yaml ...
```
