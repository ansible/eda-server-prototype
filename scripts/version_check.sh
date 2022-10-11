#!/usr/bin/env bash

# do not add version specific set lines to this file

SCRIPTS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# import common & logging
source "${SCRIPTS_DIR}"/common/logging.sh

usage() {
    log-info "Usage: $(basename "$0") <command> [command_arg]"
    log-info ""
    log-info "binaries that can be checked:"
    log-info "\t bash <version>               check for system bash version"
    log-info "\t help                         show usage"
}

help() {
    usage
}

CMD=${1:-help}
GOLDEN_VERSION="${2:-5}"

check_version() {
  local _current_version="${1}"
  local _expected_version="${2}"

  log-info "Current version: ${_current_version}"

  if [ "${_current_version}" -lt "${_expected_version}" ]; then
    log-err "version must be ${_expected_version} or higher"
    exit 1
  else
    log-info "Check successful"
  fi
}

check_bash_version() {
  local _current_version="${BASH_VERSINFO:-0}"

  check_version "${_current_version}" "${GOLDEN_VERSION}"
}

#
# execute
#
ARG=$(echo "${CMD}" |tr [a-z] [A-Z])
log-info "Checking ${CMD} version..."

case ${ARG} in
  "BASH") check_bash_version ;;
  "HELP") usage ;;
   *) usage ;;
esac