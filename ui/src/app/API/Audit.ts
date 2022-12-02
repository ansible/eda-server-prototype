import { defaultSettings } from '@app/shared/pagination';
import { getAxiosInstance } from '@app/API/baseApi';
import { AxiosResponse } from 'axios';

const auditRulesEndpoint = '/api/audit/rules_fired';
const auditHostsEndpoint = '/api/audit/hosts_changed';

export const listAuditRules = (pagination = defaultSettings): Promise<AxiosResponse> =>
  getAxiosInstance().get(auditRulesEndpoint);

export const listAuditHosts = (pagination = defaultSettings): Promise<AxiosResponse> =>
  getAxiosInstance().get(auditHostsEndpoint);
