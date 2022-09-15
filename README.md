# A UI for ansible-events

## Setting up a development environment

### Requirements

- [Docker](https://docs.docker.com/engine/install/) or [podman](https://podman.io/getting-started/installation)
- Docker-compose: `pip install docker-compose`
- [Taskfile](https://taskfile.dev/installation/)
- Git
- Python >= 3.8
- Node >= v16 (**NOTE:** node v17 does not seem to work with websockets)

NOTE podman users (only for mac and linux):

By default all dev scripts use `docker` binary. Podman users must install `podman-docker` package or run the following command:

```
sudo ln -s $(which podman) $(dirname $(which podman)/docker)
```

### 1. Clone the repository

First you need to clone the `ansible-events-ui` repository:

```shell
git clone https://github.com/benthomasson/ansible-events-ui.git
cd ansible-events-ui
```

### 2. Virtual environment

Create virtual environment and install project

```shell
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Install Ansible and `benthomasson.eda` collection:

```shell
pip install ansible
ansible-galaxy collection install benthomasson.eda
```

### 3. Services

You need to start up a PostgreSQL database sever.

```shell
task dev:services:start
```

Then run database migrations:

```shell
task dev:run:migrations
```

### 4. Start api server

```shell
task dev:api:start
```

### 5. User interface

Build UI files:

```shell
task dev:ui:start
```

Visit this url: <http://localhost:9000/api/docs#/auth/register_register_api_auth_register_post>

Click "Try it out" on `/api/auth/register`

Change email and password

Click execute

Visit this url:

- <http://localhost:8080/eda>

For API docs

- <http://localhost:8080/api/docs>
- <http://localhost:8080/api/redocs>
- <http://localhost:8080/api/openapi.json>

Also you can check the [openapi specification.](http://localhost/docs)

You have set up the development environment.

**Note:**
  Instead of running the above tasks individually, you can run the following.

```sh
task dev:start:all
```

## Run the application with docker-compose

Requires docker-compose installed. [See the documentation](https://docs.docker.com/compose/install/) for instructions. (latest stable version is recommended)

```sh
cd tools/docker
docker-compose up --build
```

NOTE Podman users:

Docker compose by default will try to expose the docker socket through a mount volume. Podman users must create a `.env` file in `tools/docker` dir defining the variable `DOCKER_SOCKET_MOUNT` with the correct path of the socket. For example:

```
# .env file
DOCKER_SOCKET_MOUNT=/run/user/1000/podman/podman.sock
```

## Run the application on Minikube

Requires:

- installation of Kubernetes CLI (kubectl)
- installation of kustomize
- installation of minikube
- installation of docker
- bash, version 5.1.* or above

Start minikube if it is not already running

```sh
minikube start
```

Check that minikube instance is up

```sh
minikube status
```

Build image and deployment files.
(If you do not provide a version as shown below docker tag will default to "latest")

```sh
task minikube:build -- 001
```

Deploy application to minikube.
(If you do not provide a version as shown below docker tag will default to "latest")

```sh
task minikube:deploy -- 001
```

Forward the webserver port to local host.
(If you do not provide a local port it will default to "8080")

```sh
task minikube:fp:ui -- 8080
```

In a second terminal run the following cmd to create a `dev` user with a password of `none2tuff`.
(You will use this to log into the console.)

```sh
scripts/createuser.sh dev_user@redhat.com none2tuff
```

Visit this url for EDA app

- <http://localhost:8080/eda>

**Note:**
  Instead of running the above build, deploy, and minikube-fp-ui tasks individually.
  It is possible to do the following, being mindful that it will use default values.

```sh
task minikube:all
```

You have set up the development environment.

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
