# A UI for ansible-events

## Setting up a development environment

### 1. Clone the repository

First you need to clone the `ansible-events-ui` repository:

```shell
  $ git clone https://github.com/benthomasson/ansible-events-ui.git
  $ cd ansible-events-ui
```

### 2. Virtual environment

Create virtual environment and install project

```shell

  $ python -m venv .venv
  $ source .venv/bin/activate
  (venv) $ pip install -e .
```

Install Ansible and `benthomasson.eda` collection:

```shell
  (venv) $ pip install ansible
  (venv) $ ansible-galaxy collection install benthomasson.eda
```

### 3. Services

You need to set up a PostgreSQL database sever. The easiest way is using the `docker-compose`:

```shell
  $ docker-compose -p ansible-events -f tools/docker/docker-compose.yml up -d postgres
```

Then run database migrations:

```shell
  $ alembic upgrade head
```

### 4. User interface

Build UI files:

```shell
  $ cd ui
  $ npm install
  $ npm run build
  $ cd ..
```

### 6. Start server

```shell
  $ ansible-events-ui
```

Visit this url: http://localhost:8080/docs#/auth/register_register_api_auth_register_post

Click "Try it out" on `/api/auth/register`

Change email and password

Click execute

Visit this url: http://localhost:8080/eda

You have set up the development environment.

## Run the application with docker-compose

Requires docker-compose installed. [See the documentation](https://docs.docker.com/compose/install/) for instructions. (latest stable version is recommended)

```sh
cd tools/docker
docker-compose up --build
```
