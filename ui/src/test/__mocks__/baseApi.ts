import MockAdapter from 'axios-mock-adapter';
import { getAxiosInstance } from '../../app/API/baseApi';

export const mockApi = new MockAdapter(getAxiosInstance());
