import { defaultSettings } from '@app/shared/pagination';
import { AxiosResponse } from 'axios';
import { getAxiosInstance } from '@app/API/baseApi';

const rulebooksEndpoint = '/api/rulebooks';

export const listRulebooks = (): Promise<AxiosResponse> => getAxiosInstance().get(rulebooksEndpoint);

export const fetchRulebook = (id: string | number): Promise<AxiosResponse> =>
  getAxiosInstance().get(`${rulebooksEndpoint}/${id}`);

export const fetchRulebookRuleSets = (id: string | number, pagination = defaultSettings): Promise<AxiosResponse> => {
  return getAxiosInstance()
    .get(`${rulebooksEndpoint}/${id}/rulesets`)
};

export const listRuleBooks = (pagination = defaultSettings): Promise<AxiosResponse> =>
  getAxiosInstance().get(rulebooksEndpoint);
