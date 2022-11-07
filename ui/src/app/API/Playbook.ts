import { defaultSettings } from '@app/shared/pagination';
import { AxiosResponse } from 'axios';
import { getAxiosInstance } from '@app/API/baseApi';

const playbooksEndpoint = '/api/playbooks';

export const listPlaybooks = (pagination = defaultSettings): Promise<AxiosResponse> =>
  getAxiosInstance().get(playbooksEndpoint);
