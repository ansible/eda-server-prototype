import { defaultSettings } from '@app/shared/pagination';
import { getAxiosInstance } from '@app/API/baseApi';
import { AxiosResponse } from 'axios';

const auditRulesEndpoint = '/api/rules';
const auditHostsEndpoint = '/api/rules';
const auditRuleEndpoint = '/api/rules';

export const listAuditRules = (pagination = defaultSettings): Promise<AxiosResponse> =>
  getAxiosInstance().get(auditRulesEndpoint);

export const listAuditHosts = (pagination = defaultSettings): Promise<AxiosResponse> =>
  getAxiosInstance().get(auditHostsEndpoint);

export const fetchAuditRuleDetails = (ruleId: string | number, pagination = defaultSettings): Promise<AxiosResponse> => {
  return getAxiosInstance().get(`${auditRuleEndpoint}/${ruleId}`);
};

export const listAuditRuleJobs = (ruleId: string | number, pagination = defaultSettings): Promise<AxiosResponse> => {
  return getAxiosInstance().get(`${auditRuleEndpoint}/${ruleId}/jobs`);
};

export const listAuditRuleEvents = (ruleId: string | number, pagination = defaultSettings): Promise<AxiosResponse> => {
  return getAxiosInstance().get(`${auditRuleEndpoint}/${ruleId}/events`);
};

export const listAuditRuleHosts = (ruleId: string | number, pagination = defaultSettings): Promise<AxiosResponse> => {
  return getAxiosInstance().get(`${auditRuleEndpoint}/${ruleId}/hosts`);
};
