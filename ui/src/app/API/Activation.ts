import {getServer, postData, removeData} from "@app/utils/utils";
import {defaultSettings} from "@app/shared/pagination";

export interface NewActivationType {
  name: string;
  rulebook_id: string,
  inventory_id: string,
  extra_var_id: string,
  project_id: string,
  working_directory?: string,
  execution_environment?: string
}

export interface IRemoveActivation {
  ids?: Array<string|number>,
  fetchData?: any,
  pagination?: PaginationConfiguration,
  resetSelectedActivations?: any
}

const activationEndpoint = 'http://' + getServer() + '/api/activation_instance';
const activationsEndpoint = 'http://' + getServer() + '/api/activation_instances';
const activationJobsEndpoint = 'http://' + getServer() + '/api/activation_instance_job_instances';
const activationLogsEndpoint = 'http://' + getServer() + '/api/activation_instance_logs/?activation_instance_id=';

export const listActivationJobs = (activationId, pagination=defaultSettings) =>
{
  return fetch(`${activationJobsEndpoint}/${activationId}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then(response => response.json());
}

export const fetchActivation = (id) => fetch(`${activationEndpoint}/${id}`, {
  headers: {
    'Content-Type': 'application/json',
  },
}).then(response => response.json())


export const listActivations = (pagination = defaultSettings) => fetch(activationsEndpoint, {
  headers: {
    'Content-Type': 'application/json',
  },
}).then(response => response.json());

export const addRulebookActivation = (activationData: NewActivationType ) => postData(activationEndpoint, activationData);

export const removeActivation = (activationId: string | number) => removeData(`${activationEndpoint}/${activationId}`);

export const fetchActivationOutput = (id: string) =>  fetch(`${activationLogsEndpoint}${id}`, {
  headers: {
    'Content-Type': 'application/json',
  },
});
