import { getAxiosInstance } from '@app/API/baseApi';
import { AxiosResponse } from 'axios';

export interface InventoryType {
  name: string;
  description?: string;
  inventory?: string;
  id?: string;
  source?: string;
}

const inventoriesEndpoint = '/api/inventories';
const inventoryEndpoint = '/api/inventory';

export const listInventories = (): Promise<AxiosResponse> => getAxiosInstance().get(inventoriesEndpoint);

export const fetchInventory = (id: string | number | undefined): Promise<AxiosResponse> =>
  getAxiosInstance().get(`${inventoryEndpoint}/${id}`);

export const addInventory = (data: InventoryType): Promise<AxiosResponse> => {
  return getAxiosInstance().post(`${inventoryEndpoint}`, data);
};

export const removeInventory = (inventoryId: string | number): Promise<AxiosResponse> =>
  getAxiosInstance().delete(`${inventoryEndpoint}/${inventoryId}`);

export const updateInventory = (inventoryId: string | number, data: InventoryType): Promise<AxiosResponse> =>
  getAxiosInstance().patch(`${inventoryEndpoint}/${inventoryId}`, data);
