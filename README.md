# A UI for ansible-events

## Setting up a development environment

Run these commands:

    git clone https://github.com/benthomasson/ansible-events-ui.git
    cd ansible-events-ui
    python3.9 -m venv .venv
    source .venv/bin/activate
    pip install -e '.[sqlite]'
    pip install ansible
    ansible-galaxy collection install benthomasson.eda
    cd ui
    npm install
    npm run build
    cd ..
    ansible-events-ui

Visit this url:

    http://localhost:8080/docs#/auth/register_register_api_auth_register_post

Click "Try it out" on /api/auth/register

Change email and password

Click execute

Visit this url:

    http://localhost:8080/eda

You have set up the development environment.

## Run the application with docker-compose

Requires docker-compose installed. [See the documentation](https://docs.docker.com/compose/install/) for instructions.

```sh
cd tools/docker
docker-compose up --build
```
