import {getServer, postData, removeData} from "@app/utils/utils";
import {defaultSettings} from "@app/shared/pagination";

export interface NewJobType {
  name?: string;
  playbook_id: string;
  inventory_id: string;
  extra_var_id: string;
}

const jobEndpoint = 'http://' + getServer() + '/api/job_instance';
const jobsEndpoint = 'http://' + getServer() + '/api/job_instances';
const eventsEndpoint = 'http://' + getServer() + '/api/job_instance_events';

export const fetchJob = (id: string|number|undefined) =>  fetch(`${jobEndpoint}/${id}`, {
  headers: {
    'Content-Type': 'application/json',
  },
}).then(response => response.json());

export const fetchJobEvents = (id: string|number) => fetch(`${eventsEndpoint}/${id}`, {
  headers: {
    'Content-Type': 'application/json',
  },
}).then(response => response.json());

export const addJob = (jobData: NewJobType) =>  postData(jobEndpoint, jobData);

export const listJobs = (pagination = defaultSettings) => fetch(jobsEndpoint, {
  headers: {
    'Content-Type': 'application/json',
  },
}).then(response => response.json());

export const removeJob = (jobId) => removeData(`${jobEndpoint}/${jobId}`);
