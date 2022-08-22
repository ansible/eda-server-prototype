#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

#
#
# Assumes environment variables have been set:
#   - ANSIBLE_EVENTS_UI_HOME
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
    log-info "ui-start            build and start EDA UI"
    log-info "ui-stop             stop EDA UI"
    log-info "ui-restart          rebuild and restart EDA UI"
    log-info "start-all           start both the services and EDA UI"
    log-info "stop-all            stop both the services and EDA UI"
    log-info "restart-all         restart both the services and EDA UI"
    log-info "help                gives this usage output"
}

help() {
    usage
}
CMD=${1:-help}
DEBUG=${DEBUG:-false}

DEV_SCRIPTS_PATH=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

DEV_USER="${DEV_USER:=demo_user@redhat.com}"
DEV_PASS="${DEV_PASS:=none2tuff}"

SERVICE_CONTAINER_NAMES=( ansible-events_postgres_1 )

# import common & logging
source "$DEV_SCRIPTS_PATH"/common/logging.sh
source "$DEV_SCRIPTS_PATH"/common/utils.sh

trap handle_errors ERR

handle_errors() {
  log-err "An error occurred on or around line ${BASH_LINENO[0]}. Unable to continue."
  exit 1
}

# check for these env variables
log-info "Checking environment variables..."
check_vars ANSIBLE_EVENTS_UI_HOME

check_uvicorn_status() {
  local _url=http://localhost:8080/eda/
  local _timeout=10
  local _count=0

  while [[ $_count != $_timeout ]]; do
    http_code=$(curl -w %{http_code} -s --output /dev/null $_url)

    if [ 200 == "$http_code" ]; then
      return 0
    fi
    sleep 2
    _count=$((_count + 1))
  done

  return 1
}

add_demo_user() {
  log-info "Adding demo user: ${DEV_USER}, pass: ${DEV_PASS}"
  log-debug "scripts/createuser.sh ${DEV_USER} ${DEV_PASS}"
  "${DEV_SCRIPTS_PATH}"/createuser.sh ${DEV_USER} ${DEV_PASS}
}

start-events-services() {
  log-info "Starting Event Services..."
  cd "${ANSIBLE_EVENTS_UI_HOME}"

  for container in "${SERVICE_CONTAINER_NAMES[@]}"; do
    if [[ $(docker inspect --format '{{json .State.Running}}' "$container") = "true" ]]; then
      log-warn "$container service is already running"
    else
      log-debug "docker-compose -p ansible-events -f tools/docker/docker-compose.yml up -d postgres"
      docker-compose -p ansible-events -f tools/docker/docker-compose.yml up -d postgres

      until [ "$(docker inspect -f {{.State.Health.Status}} "$container")" == "healthy" ]; do
        sleep 1;
      done;

      log-debug "alembic upgrade head"
      alembic upgrade head
    fi
  done
}

stop-events-services() {
  log-info "Stopping Event Services..."
  cd "${ANSIBLE_EVENTS_UI_HOME}"

  for container in "${SERVICE_CONTAINER_NAMES[@]}"; do
    if [ $(docker inspect --format '{{json .State.Running}}' "$container") = "true" ]; then
      docker stop "$container" > /dev/null 2>&1
    else
      log-warn "$container is not running"
    fi
  done
}

start-events-ui() {
  cd "${ANSIBLE_EVENTS_UI_HOME}"/ui

  log-info "Building Event UI..."
  log-debug "npm install"
  npm install

  log-info "Starting Event UI..."
  log-debug "npm run build"
  npm run build

  cd "${ANSIBLE_EVENTS_UI_HOME}"
  ansible-events-ui &
  if check_uvicorn_status; then
    log-info "Uvicorn started"
  else
    log-err "timed out waiting for Uvicorn server to become ready"
    return 1
  fi
}

# shellcheck disable=SC2120
stop-events-ui() {
  log-info "Stopping Event UI..."
  log-debug "ps -ef | grep ansible-events-ui | grep -v grep | awk '{print $2}' | xargs kill"
  pgrep ansible-events-ui | grep -v grep | awk '{print $2}' | xargs kill

  if lsof -i:8080 >/dev/null 2>&1; then
    log-debug "killing port tcp:8080"
    kill -9 $(lsof -t -i tcp:8080) >/dev/null 2>&1
  fi
}

start-events-all() {
  start-events-services
  start-events-ui
  add_demo_user
}

stop-events-all() {
 stop-events-services
 stop-events-ui
}

# ---execute---
ARG=$(echo "${CMD}" |tr [a-z] [A-Z])

case ${ARG} in
  "SERVICES-START")
    start-events-services ;;
  "SERVICES-STOP")
    stop-events-services ;;
  "SERVICES-RESTART")
    stop-events-services
    start-events-services ;;
  "UI-START")
    start-events-ui ;;
  "UI-STOP")
    stop-events-ui ;;
  "UI-RESTART")
    stop-events-ui
    start-events-ui ;;
  "START-ALL")
    start-events-all ;;
  "STOP-ALL")
    stop-events-all ;;
  "RESTART-ALL")
    stop-events-all
    start-events-all ;;
 "HELP") usage ;;
 *) usage ;;
esac