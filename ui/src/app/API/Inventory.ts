import { defaultSettings } from '@app/shared/pagination';
import { getAxiosInstance } from '@app/API/baseApi';
import { AxiosResponse } from 'axios';

export interface NewInventoryType {
  name: string;
  description?: string;
  inventory?: string;
}

const inventoriesEndpoint = '/api/inventories';
const inventoryEndpoint = '/api/inventory';

export const listInventories = (pagination = defaultSettings): Promise<AxiosResponse> =>
  getAxiosInstance().get(inventoriesEndpoint);

export const fetchInventory = (id: string | number | undefined): Promise<AxiosResponse> =>
  getAxiosInstance().get(`${inventoryEndpoint}/${id}`);

export const addInventory = (data: NewInventoryType): Promise<AxiosResponse> =>
  getAxiosInstance().post(inventoryEndpoint, data);
export const removeInventory = (inventoryId: string | number): Promise<AxiosResponse> =>
  getAxiosInstance().delete(`${inventoryEndpoint}/${inventoryId}`);
