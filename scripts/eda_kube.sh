#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

SCRIPTS_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_DIR="${SCRIPTS_DIR}/.."

CMD=${1:-help}
VERSION=${2:-'latest'}
UI_LOCAL_PORT=${2:-8080}

export DEBUG=${DEBUG:-false}

# import common & logging
source "${SCRIPTS_DIR}"/common/logging.sh
source "${SCRIPTS_DIR}"/common/utils.sh

trap handle_errors ERR

handle_errors() {
  log-err "An error occurred on or around line ${BASH_LINENO[0]}. Unable to continue."
  exit 1
}

# deployment dir
DEPLOY_DIR="${PROJECT_DIR}"/tools/deploy

# minikube namespace
NAMESPACE=${NAMESPACE:-eda-project}

usage() {
    log-info "Usage: $(basename "$0") <command> [command_arg]"
    log-info ""
    log-info "commands:"
    log-info "\t build <version>               build and push image to minikube"
    log-info "\t deploy <version>              build deployment and deploy to minikube"
    log-info "\t clean                         remove deployment directory and all EDA resource from minikube"
    log-info "\t port-forward-ui <port>        forward local port to Events UI (default: 8080)"
    log-info "\t add-dev-user                  add user: dev_user@redhat.com, password: none2tuff"
    log-info "\t load-rbac-data                load up RBAC users and roles"
    log-info "\t help                          show usage"
}

help() {
    usage
}

build-deployment() {
  local _ui_image="eda-frontend:${1}"
  local _api_image="eda-server:${1}"

  log-info "Using Deployment Directory: ${DEPLOY_DIR}/temp"

  remove-deployment-tempdir
  [ -d "${DEPLOY_DIR}"/temp ] || mkdir "${DEPLOY_DIR}"/temp

  log-debug "kustomize edit set image eda-server=${_api_image}"
  cd "${DEPLOY_DIR}"/eda-server
  kustomize edit set image "eda-server=${_api_image}"

  log-debug "kustomize edit set image eda-frontend=${_ui_image}"
  cd "${DEPLOY_DIR}"/eda-frontend
  kustomize edit set image "eda-frontend=${_ui_image}"

  cd "${PROJECT_DIR}"
  log-debug "kustomize build ${DEPLOY_DIR} -o ${DEPLOY_DIR}/temp"
  kustomize build "${DEPLOY_DIR}" -o "${DEPLOY_DIR}/temp"
}

build-frontend() {
  local _image="eda-frontend:${1}"

  log-info "minikube image build . -t ${_image} -f tools/docker/nginx/Dockerfile"
  minikube image build . -t "${_image}" -f tools/docker/nginx/Dockerfile
}

build-server() {
  local _image="eda-server:${1}"

  log-info "minikube image build . -t ${_image} -f tools/docker/Dockerfile"
  minikube image build . -t "${_image}" -f tools/docker/Dockerfile
}

build-all() {
  build-frontend "${1}"
  build-server "${1}"
  build-deployment "${1}"
}

remove-image() {
  local _image_name="${1}"

  if minikube image ls | grep "${_image_name}" &> /dev/null; then
    log-info "Removing image ${_image_name} from minikube registry"
    log-debug "minikube image rm ${_image_name}"
    minikube image rm "${_image_name}"
  fi
}

remove-deployment-tempdir() {
  if [ -d "${DEPLOY_DIR}"/temp ]; then
    log-debug "rm -rf ${DEPLOY_DIR}/temp"
    rm -rf "${DEPLOY_DIR}"/temp
  else
    log-debug "${DEPLOY_DIR}/temp does not exist"
  fi
}

deploy() {
  local _image="${1}"

  if [ -d "${DEPLOY_DIR}"/temp ]; then
    if ! kubectl get ns -o jsonpath='{..name}'| grep "${NAMESPACE}" &> /dev/null; then
      log-debug "kubectl create namespace ${NAMESPACE}"
      kubectl create namespace "${NAMESPACE}"
    fi

    kubectl config set-context --current --namespace="${NAMESPACE}"

    log-info "deploying eda to ${NAMESPACE}"
    log-debug "kubectl apply -f ${DEPLOY_DIR}/temp"
    kubectl apply -f "${DEPLOY_DIR}"/temp

  else
    log-err "You must run 'minikube:build' before running minikube:deploy"
  fi
}

clean-deployment() {
  log-info "cleaning minikube deployment..."
  if kubectl get ns -o jsonpath='{..name}'| grep "${NAMESPACE}" &> /dev/null; then
    log-debug "kubectl delete all -l 'app in (eda-server, eda-frontend, eda-postgres)' -n ${NAMESPACE}"
    kubectl delete all -l 'app in (eda-server, eda-frontend, eda-postgres)' -n "${NAMESPACE}"
    log-debug "kubectl delete pvc --all --grace-period=0 --force -n ${NAMESPACE}"
    kubectl delete pvc --all --grace-period=0 --force -n "${NAMESPACE}"
    log-debug "kubectl delete pv --all --grace-period=0 --force -n ${NAMESPACE}"
    kubectl delete pv --all --grace-period=0 --force -n "${NAMESPACE}"
  else
    log-debug "${NAMESPACE} does not exist"
  fi

  remove-deployment-tempdir

  remove-image postgres:13
  remove-image nginx:"${VERSION}"
  remove-image eda-server:"${VERSION}"
  remove-image eda-frontend:"${VERSION}"
}

# forward localhost port to pod
port-forward() {
  local _local_port=${2}
  local _svc_name=${1}
  local _svc_port=${3}

  log-info "kubectl port-forward svc/${_svc_name} ${_local_port}:${_svc_port}"
  kubectl port-forward "svc/${_svc_name}" "${_local_port}":"${_svc_port}"
}

port-forward-ui() {
  local _local_port=${1}
  local _svc_name=eda-frontend
  local _svc_port=8080

  log-debug "port-forward ${_svc_name} ${_local_port} ${_svc_port}"
  port-forward "${_svc_name}" "${_local_port}" "${_svc_port}"
}

add-dev-user() {
  local user="dev_user@redhat.com"
  local eda_server_pod_name=$(kubectl get pod -l app=eda-server -o jsonpath="{.items[0].metadata.name}")

  log-info "Adding development admin user: dev_user@redhat.com"
  log-debug "kubectl exec "${eda_server_pod_name}" -- scripts/adduser.py -S --password "${password}" "${user}""
  kubectl exec "${eda_server_pod_name}" -- scripts/adduser.py -S --password "${password}" "${user}"
}

load-rbac-data() {
  local data_file=tools/initial_data.yml
  local eda_server_pod_name=$(kubectl get pod -l app=eda-server -o jsonpath="{.items[0].metadata.name}")

  log-info "Adding development admin user: dev_user@redhat.com"
  log-debug "kubectl exec "${eda_server_pod_name}" -- scripts/load_data.py ${data_file}"
  kubectl exec "${eda_server_pod_name}" -- scripts/load_data.py "${data_file}"
}

#
# execute
#
case ${CMD} in
  "build") build-all "${VERSION}" ;;
  "clean") clean-deployment "${VERSION}";;
  "deploy") deploy "${VERSION}" ;;
  "port-forward-ui") port-forward-ui "${UI_LOCAL_PORT}" ;;
  "add-dev-user") add-dev-user ;;
  "load-rbac-data") load-rbac-data ;;
  "help") usage ;;
   *) usage ;;
esac
