import { defaultSettings } from '@app/shared/pagination';
import { AxiosResponse } from 'axios';
import { getAxiosInstance } from '@app/API/baseApi';

const rulesEndpoint = '/api/rules';

export const fetchRule = (ruleId: string | number, pagination = defaultSettings): Promise<AxiosResponse> => {
  return getAxiosInstance().get(`${rulesEndpoint}/${ruleId}`);
};

export const listRules = (pagination = defaultSettings): Promise<AxiosResponse> =>
  getAxiosInstance().get(rulesEndpoint);
