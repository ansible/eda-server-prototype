import { defaultSettings } from '@app/shared/pagination';
import { getAxiosInstance } from '@app/API/baseApi';
import { AxiosResponse } from 'axios';

export interface NewActivationType {
  name: string;
  rulebook_id: string;
  inventory_id: string;
  extra_var_id: string;
  project_id: string;
  working_directory?: string;
  execution_environment?: string;
}

export interface IRemoveActivation {
  ids?: Array<string | number>;
  fetchData?: any;
  pagination?: PaginationConfiguration;
  resetSelectedActivations?: any;
}

const activationEndpoint = '/api/activation_instance';
const activationsEndpoint = '/api/activation_instances';
const activationJobsEndpoint = '/api/activation_instance_job_instances';
const activationLogsEndpoint = '/api/activation_instance_logs/?activation_instance_id=';

export const listActivationJobs = (
  activationId: string | number,
  pagination = defaultSettings
): Promise<AxiosResponse> => {
  return getAxiosInstance().get(`${activationJobsEndpoint}/${activationId}`);
};

export const fetchActivation = (id: string | number | undefined): Promise<AxiosResponse> =>
  getAxiosInstance().get(`${activationEndpoint}/${id}`);

export const listActivations = (pagination = defaultSettings): Promise<AxiosResponse> =>
  getAxiosInstance().get(activationsEndpoint);

export const addRulebookActivation = (activationData: NewActivationType) =>
  getAxiosInstance().post(activationEndpoint, activationData);

export const removeActivation = (activationId: string | number): Promise<AxiosResponse> =>
  getAxiosInstance().delete(`${activationEndpoint}/${activationId}`);

export const fetchActivationOutput = (id: string): Promise<AxiosResponse> =>
  getAxiosInstance().get(`${activationLogsEndpoint}${id}`);
