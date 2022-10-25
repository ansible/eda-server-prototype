import axios, { AxiosRequestConfig, AxiosInstance } from 'axios';
import { stringify } from 'qs';

export interface ErrorResponse {
  headers?: Headers;
}

export interface ServerError {
  response?: ErrorResponse;
  status?: 403 | 404 | 401 | 400 | 429 | 500 | 200; // not a complete list, replace by library with complete interface
  config?: AxiosRequestConfig;
}

const createAxiosInstance = () => {
  return axios.create({
    paramsSerializer: (params) => stringify(params),
  });
};

const axiosInstance: AxiosInstance = createAxiosInstance();

export function getAxiosInstance(): AxiosInstance {
  return axiosInstance;
}
