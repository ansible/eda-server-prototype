#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

#
#
# Assumes environment variables have been set:
#   - EDA_PROJECT_HOME
#
# Optional environment variables
#   - DEV_USER (default: demo_user@redhat.com)
#   - DEV_PASS (default: none2tuff)
#   - DEBUG=true|false (default is false)
#

usage() {
    log-info "Usage: $(basename "$0") <command>"
    log-info ""
    log-info "services-start      start service containers"
    log-info "services-stop       stop service containers"
    log-info "services-restart    restart service container"
    log-info "service-clean       remove container/images and volumes"
    log-info "db-migrations       run database migrations"
    log-info "ui-start            build and start EDA UI"
    log-info "ui-stop             stop EDA UI"
    log-info "ui-restart          rebuild and restart EDA UI"
    log-info "api-start           start EDA API"
    log-info "api-stop            stop EDA API"
    log-info "api-restart         restart EDA API"
    log-info "start-all           start both the services and EDA UI"
    log-info "stop-all            stop both the services and EDA UI"
    log-info "restart-all         restart both the services and EDA UI"
    log-info "add-dev-user        add dev user(defaults): user dev_user@redhat.com, password: none2tuff"
    log-info "load-rbac-data      load in test RBAC users and roles"
    log-info "help                gives this usage output"
}

help() {
    usage
}
CMD=${1:-help}
DEBUG=${DEBUG:-false}

EDA_PI_PORT=9000

DEV_SCRIPTS_PATH=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

DEV_USER="${DEV_USER:=dev_user@redhat.com}"
DEV_PASS="${DEV_PASS:=none2tuff}"

EDA_PROJECT_HOME="${DEV_SCRIPTS_PATH}/.."

# import common & logging
source "$DEV_SCRIPTS_PATH"/common/logging.sh
source "$DEV_SCRIPTS_PATH"/common/utils.sh

trap handle_errors ERR

handle_errors() {
  log-err "An error occurred on or around line ${BASH_LINENO[0]}. Unable to continue."
  exit 1
}

check_uvicorn_status() {
  local _url=http://localhost:"${EDA_PI_PORT}"/api/docs
  local _timeout=10
  local _count=0

  while [[ $_count != "$_timeout" ]]; do
    http_code=$(curl -w %{http_code} -s --output /dev/null $_url)

    if [ 200 == "$http_code" ]; then
      return 0
    fi
    sleep 2
    _count=$((_count + 1))
  done

  return 1
}

add-dev-user() {
  log-info "Adding dev user: ${DEV_USER}, pass: ${DEV_PASS}"
  log-debug "${DEV_SCRIPTS_PATH}/adduser.py -S --password ${DEV_PASS} ${DEV_USER}"
  "${DEV_SCRIPTS_PATH}"/adduser.py -S --password "${DEV_PASS}" "${DEV_USER}"
}

load-rbac-data() {
  local data_file=tools/initial_data.yml
  log-info "Loading RBAC data..."
  log-debug "${DEV_SCRIPTS_PATH}/load_data.py ${data_file}"
  "${DEV_SCRIPTS_PATH}"/load_data.py "${data_file}"
}

start-events-services() {
  log-info "Starting EDA Services (eda-postgres)"
  cd "${EDA_PROJECT_HOME}"

  if [[ $(docker inspect --format '{{json .State.Running}}' eda-postgres) = "true" ]]; then
    log-warn "eda-postgres service is already running"
  else
    log-debug "docker-compose -p eda-server -f tools/docker/docker-compose.yml up -d postgres"
    docker-compose -p eda-server -f tools/docker/docker-compose.yml up -d postgres

    #
    # Podman versions previous to v4 use a different string variation for health check.
    #
    # Reference:
    #      https://github.com/containers/podman/issues/11645
    #
    # Default is to check if podman is installed. If true then use podman.
    #
    local heath_check=".State.Health.Status"

    if which podman &> /dev/null; then
      _podman_version=$(podman -v)
      _podman_major_version=$(podman -v | awk '{print substr($3,0,1)}')

      log-info "Using podman installation"
      log-debug "podman version: ${_podman_version}"

      if [ "${_podman_major_version}" -lt "4" ]; then
        heath_check=".State.Healthcheck.Status"
        log-debug "Set healthcheck flag: ${heath_check}"
      fi
    elif which docker &> /dev/null; then
      heath_check="${heath_check}"
      log-info "Using docker installation"
      log-debug "docker version: $(docker -v)"
      log-debug "Set healthcheck flag: ${heath_check}"
    fi

    local _cnt=0
    local _timeout=15
    until [ "$(docker inspect -f "{{${heath_check}}}" eda-postgres)" == "healthy" ] || [ "${_cnt}" -eq "${_timeout}" ]; do
      log-debug "Healthcheck waiting...[$((++_cnt))s]"
      sleep 1;

      if [ "${_cnt}" -eq "${_timeout}" ]; then
        log-err "timeout waiting for postgres service!"
        exit 1
      fi
    done;
  fi
}

db-migrations() {
  set +e
  local -i rc=0
  local alembic_out
  if [[ $(docker inspect --format '{{json .State.Running}}' eda-postgres) = "true" ]]; then
    log-info "Running DB migrations..."
    log-debug "alembic upgrade head"
    alembic_out=$(alembic upgrade head)
    rc=$?
    if grep -q 'FAILED: Multiple head revisions are present' <<< "${alembic_out}" ; then
      alembic_out=$(alembic heads --verbose)
      log-err "${alembic_out}"
    fi
  else
    log-warn "eda-postgres service is not running!"
  fi

  set -e
  return $rc
}

stop-events-services() {
  log-info "Stopping EDA Services (eda-postgres)"
  cd "${EDA_PROJECT_HOME}"

  if [[ $(docker inspect --format '{{json .State.Running}}' eda-postgres) = "true" ]]; then
    log-debug "docker-compose -p eda-server -f tools/docker/docker-compose.yml down"
    docker-compose -p eda-server -f tools/docker/docker-compose.yml down
  fi
}

clean-events-services() {
  local _volume_name="eda-server_postgres_data"

  log-info "Cleaning up EDA Services (postgres)"
  if docker images --format '{{.Repository}}' postgres| grep postgres > /dev/null 2>&1; then
    log-debug "docker rmi -f postgres:13"
    docker rmi -f postgres:13 > /dev/null 2>&1
  fi

  if docker volume inspect -f '{{.Name}}' "${_volume_name}"| grep "${_volume_name}"> /dev/null 2>&1; then
    log-debug "docker volume rm $_volume_name"
    docker volume rm "${_volume_name}" > /dev/null 2>&1
  fi
}

start-events-ui() {
  cd "${EDA_PROJECT_HOME}"/ui

  log-info "Installing npm dependencies..."
  log-debug "npm install"
  npm install

  log-info "Starting UI (eda-frontend)"
  log-debug "npm run start:dev"
  npm run start:dev &
}

# shellcheck disable=SC2046
stop-events-ui() {
  log-info "Stopping UI (eda-frontend)"

  if pgrep -f 'npm run start:dev' >/dev/null 2>&1; then
    log-debug "kill -9 \$(pgrep -f 'npm run start:dev')"
    kill -9 $(pgrep -f 'npm run start:dev') >/dev/null 2>&1
  fi

  if pgrep -f 'webpack' >/dev/null 2>&1; then
    kill -9 $(pgrep -f 'webpack') >/dev/null 2>&1
  fi
}

start-events-api() {
  log-info "Starting API (eda-server)"
  cd "${EDA_PROJECT_HOME}"
  log-debug "eda-server &"
  eda-server &
}

# shellcheck disable=SC2046
stop-events-api() {
  log-info "Stopping API (eda-server)"

  if pgrep -f eda-server >/dev/null 2>&1; then
    log-debug "kill -9 \$(pgrep -f eda-server)"
    kill -9 $(pgrep -f eda-server) >/dev/null 2>&1
  fi

  if lsof -i:"${EDA_PI_PORT}" >/dev/null 2>&1; then
    log-debug "killing port tcp:${EDA_PI_PORT}"
    kill -9 $(lsof -t -i tcp:"${EDA_PI_PORT}") >/dev/null 2>&1
  fi
}

start-events-all() {
  start-events-services
  db-migrations
  start-events-api
  start-events-ui
}

stop-events-all() {
 stop-events-services
 stop-events-api
 stop-events-ui
}

# ---execute---
ARG=$(echo "${CMD}" |tr [a-z] [A-Z])

case ${ARG} in
  "SERVICES-START")
    start-events-services ;;
  "SERVICES-STOP")
    stop-events-services ;;
  "SERVICES-CLEAN")
    clean-events-services ;;
  "SERVICES-RESTART")
    stop-events-services
    start-events-services ;;
  "DB-MIGRATIONS")
    db-migrations ;;
  "UI-START")
    start-events-ui ;;
  "UI-STOP")
    stop-events-ui ;;
  "UI-RESTART")
    stop-events-ui
    start-events-ui ;;
  "API-START")
    start-events-api ;;
  "API-STOP")
    stop-events-api ;;
  "API-RESTART")
    stop-events-api
    start-events-api ;;
  "START-ALL")
    start-events-all ;;
  "STOP-ALL")
    stop-events-all ;;
  "RESTART-ALL")
    stop-events-all
    start-events-all ;;
  "ADD-DEV-USER")
    add-dev-user ;;
  "LOAD-RBAC-DATA")
    load-rbac-data ;;
 "HELP") usage ;;
 *) usage ;;
esac
