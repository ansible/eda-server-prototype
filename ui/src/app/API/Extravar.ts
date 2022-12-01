import { getAxiosInstance } from '@app/API/baseApi';
import { AxiosResponse } from 'axios';

const extravarsEndpoint = '/api/extra_vars/';
const extravarEndpoint = '/api/extra_var';

export const listExtraVars = (): Promise<AxiosResponse> => getAxiosInstance().get(extravarsEndpoint);

export const fetchRuleVars = (varname: string): Promise<AxiosResponse> => {
  return getAxiosInstance().get(`${extravarEndpoint}/${varname}`);
};

export const fetchExtraVar = (id: string | number): Promise<AxiosResponse> =>
  getAxiosInstance().get(`${extravarEndpoint}/${id}`);
