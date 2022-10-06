# Getting started

Before performing any of the deployment steps, please use Git to clone this repository and *cd* into the repository folder:

    git clone https://github.com/ansible/eda-server.git
    cd eda-server

# Deploy using docker-compose

The deployment based on docker/podman and docker-compose is the recommended method for linux users.

## Requirements

- Container runtime installed and configured ([Podman](https://podman.io/getting-started/installation) or [Docker](https://docs.docker.com/engine/install/))
- [Docker-compose](https://docs.docker.com/compose/install/other/)

      pip install docker-compose

- The `docker` binary will be used during deployment by default. Podman users should install the `podman-docker` package, or manually create a symlink to the `podman` binary:

      sudo ln -s $(which podman) $(dirname $(which podman))/docker

**NOTE Mac OS + podman users**

Due to issues with volume mounting, the deployment based on docker-compose is not supported yet for Mac OS + podman users. Please refer to the
[minikube deployment](#deploy-using-minikube-and-taskfile) section for an alternative option.

## Deployment

You can follow the below steps to spin up an instance of eda-server within minutes.
Please read through the [Requirements](#requirements) section carefully before attempting any of the below deployment instructions.

***
**Podman users only:**

- `DOCKER_HOST` environment variable must be defined pointing to the podman socket to be able to use `docker-compose`.  Example:

      export DOCKER_HOST=unix:///run/user/$UID/podman/podman.sock

- Ensure the `podman.socket` service is enabled and running:

      systemctl --user enable --now podman.socket

- docker-compose will try to expose the Docker socket through a mount volume. Podman users must create a `.env` file in the `tools/docker` directory which defines the variable `DOCKER_SOCKET_MOUNT` with the correct path and UID to the socket file (or export the environment variable):

      # tools/docker/.env file
      DOCKER_SOCKET_MOUNT=/run/user/<UID>/podman/podman.sock

***

1. Navigate to the `tools/docker` directory and run `docker-compose`:

       cd tools/docker
       docker-compose up -d --build

2. Create a superuser account for `user@example.com` and password `test`:

       docker|podman exec eda-server scripts/adduser.py -S --password test admin@example.com

You can now access the UI at <http://localhost:8080/eda/> using the above credentials.

# Deploy using Minikube and Taskfile

Minikube is the recommemded method for Mac OS users

## Requirements

- [Kubernetes CLI (kubectl)](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)
- [kustomize](https://kubectl.docs.kubernetes.io/installation/kustomize/)
- [minikube](https://minikube.sigs.k8s.io/docs/start/)
- [Taskfile](https://taskfile.dev/installation/#binary)
- bash, version 5.1.* or above

**NOTE for Mac OS users**
Mac OS ships a very old version of bash. It must be updated:

```sh
brew install bash
```

## Deployment

1. Start minikube if it is not already running:

       minikube start

2. Ensure minikube instance is up and running:

       minikube status

3. Run the deployment:

       task minikube:all

4. Forward the webserver port to the localhost:

       task minikube:fp:ui

**Note**: For fedora, the binary may be `go-task`.

5. Create a superuser account for `user@example.com` and password `test`:

        kubectl exec $(kubectl get pod -l app=eda-server -o jsonpath="{.items[0].metadata.name}") -- scripts/adduser.py -S --password test user@example.com

You can now access the UI at <http://localhost:8080/eda/> using the above credentials.
