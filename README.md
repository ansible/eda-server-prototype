# A UI for ansible-events

## Setting up a development environment

### 1. Install taskfile

[Taskfile](https://taskfile.dev/) is a task runner that aims to be simpler and easier
replacement for a GNU Make.

Install taskfile following the [installation guide](https://taskfile.dev/installation/).

### 2. Clone the repository

First you need to clone the `ansible-events-ui` repository:

```shell
git clone https://github.com/benthomasson/ansible-events-ui.git
cd ansible-events-ui
```

### 3. Virtual environment

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

### 4. Services

You need to set up a PostgreSQL database sever. The easiest way is using the `docker-compose`:

```shell
docker-compose -p ansible-events -f tools/docker/docker-compose.yml up -d postgres
```

Then run database migrations:

```shell
alembic upgrade head
```

### 5. User interface

Build UI files (requires Node >= v16):

```shell
cd ui
npm install
npm run build
cd ..
```

### 6. Start server

```shell
ansible-events-ui
```

Visit this url: <http://localhost/api/docs/auth/register_register_api_auth_register_post>

Click "Try it out" on `/api/auth/register`

Change email and password

Click execute

Visit this url: http://localhost/eda

Also you can check the [openapi specification.](http://localhost/docs)

You have set up the development environment.

## Run the application with docker-compose

Requires docker-compose installed. [See the documentation](https://docs.docker.com/compose/install/) for instructions. (latest stable version is recommended)

```sh
cd tools/docker
docker-compose up --build
```

## Run the application on Minikube

Requires:
* installation of Kubernetes CLI (kubectl)
* installation of kustomize
* installation of minikube
* installation of docker
* bash, version 5.1.* or above

Start minikube if it is not already running
```sh
minikube start
```
Check that minikube instance is up
```sh
minikube status
```

Build image and deployment files.
(If you do not provide an image:version as shown below it will default to "eda:latest")
```sh
task minikube:build -- eda:001
```

Deploy application to minikube.
(If you do not provide an image:version as shown below it will default to "eda:latest")
```sh
task minikube:deploy -- eda:001
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

Visit this url: http://localhost/eda

- **Note:** 
  Instead of running the above build, deploy, and minikube-fp-ui tasks individually. 
  It is possible to do the following, being mindful that it will use default values.
```sh
$ task minikube:all
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
