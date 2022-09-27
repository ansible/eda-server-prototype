#!/usr/bin/env bash

check_vars() {
    # Variable validation.
    #
    # Args: ($@) - 1 or many variable(s) to check
    #
    local _var_names=("$@")

    for var_name in "${_var_names[@]}"; do
        if  [[ -v $var_name ]]; then
          log-debug "${var_name}=${!var_name}"
        else
          log-err "Environment variable $var_name is not set! Unable to continue."
          exit 1
        fi
    done
}

check_bash_version() {
  local _version="${1:-5}"

  if [ ! "${BASH_VERSINFO:-0}" -ge "${_version}" ]; then
    log-err "bash version must be 5 or above"
    log-err "Current bash version: ${BASH_VERSION}"
    exit 1
  fi
}
