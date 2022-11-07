import { defaultSettings } from '@app/shared/pagination';
import { AxiosResponse } from 'axios';
import { getAxiosInstance } from '@app/API/baseApi';

export interface NewJobType {
  name?: string;
  playbook_id: string;
  inventory_id: string;
  extra_var_id: string;
}

const jobEndpoint = '/api/job_instance';
const jobsEndpoint = '/api/job_instances';
const eventsEndpoint = '/api/job_instance_events';

export const fetchJob = (id: string | number | undefined): Promise<AxiosResponse> =>
  getAxiosInstance().get(`${jobEndpoint}/${id}`);

export const fetchJobEvents = (id: string | number): Promise<AxiosResponse> =>
  getAxiosInstance().get(`${eventsEndpoint}/${id}`);

export const addJob = (jobData: NewJobType): Promise<AxiosResponse> => getAxiosInstance().post(jobEndpoint, jobData);

export const listJobs = (pagination = defaultSettings): Promise<AxiosResponse> => getAxiosInstance().get(jobsEndpoint);

export const removeJob = (jobId: string | number): Promise<AxiosResponse> =>
  getAxiosInstance().delete(`${jobEndpoint}/${jobId}`);
