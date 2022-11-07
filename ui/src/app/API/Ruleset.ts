import { defaultSettings } from '@app/shared/pagination';
import { getAxiosInstance } from '@app/API/baseApi';
import { AxiosResponse } from 'axios';

const rulesetsEndpoint = '/api/rulesets';
const rulesEndpoint = '/api/rulebook_json';
const sourcesEndpoint = '/api/rulebook_json';

export const listRulesets = (pagination = defaultSettings): Promise<AxiosResponse> => {
  return getAxiosInstance().get(`${rulesetsEndpoint}`);
};

export const fetchRuleset = (id: string | number): Promise<AxiosResponse> => {
  return getAxiosInstance().get(`${rulesetsEndpoint}/${id}`);
};

export const fetchRulesetRules = (id: string | number, pagination = defaultSettings): Promise<AxiosResponse> => {
  return getAxiosInstance()
    .get(`${rulesEndpoint}/${id}`)
    .then((data) =>
      data?.data && data.data.rulesets && data.data.rulesets.length > 0 ? data.data.rulesets[0].rules : []
    );
};

export const fetchRulesetSources = (id: string | number, pagination = defaultSettings): Promise<AxiosResponse> => {
  return getAxiosInstance()
    .get(`${sourcesEndpoint}/${id}`)
    .then((data) =>
      data?.data && data.data.rulesets && data.data.rulesets.length > 0 ? data.data.rulesets[0].sources : []
    );
};
