import { defaultSettings } from '@app/shared/pagination';
import { getAxiosInstance } from '@app/API/baseApi';
import { AxiosResponse } from 'axios';

const actionsRulesEndpoint = '/api/audit/rules_fired';
const actionsHostsEndpoint = '/api/audit/hosts_changed';
const actionsRuleEndpoint = '/api/audit/rule';

export const listActionsRules = (pagination = defaultSettings): Promise<AxiosResponse> =>
  getAxiosInstance().get(actionsRulesEndpoint);

export const listActionsHosts = (pagination = defaultSettings): Promise<AxiosResponse> =>
  getAxiosInstance().get(actionsHostsEndpoint);

export const fetchActionsRuleDetails = (ruleId: string | number, pagination = defaultSettings): Promise<AxiosResponse> =>
  getAxiosInstance().get(`${actionsRuleEndpoint}/${ruleId}/details`);

export const listActionsRuleJobs = (ruleId: string | number, pagination = defaultSettings): Promise<AxiosResponse> =>
  getAxiosInstance().get(`${actionsRuleEndpoint}/${ruleId}/jobs`);

export const listActionsRuleEvents = (ruleId: string | number, pagination = defaultSettings): Promise<AxiosResponse> =>
  getAxiosInstance().get(`${actionsRuleEndpoint}/${ruleId}/events`);

export const listActionsRuleHosts = (ruleId: string | number, pagination = defaultSettings): Promise<AxiosResponse> =>
  getAxiosInstance().get(`${actionsRuleEndpoint}/${ruleId}/hosts`);
