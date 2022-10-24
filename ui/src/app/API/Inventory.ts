import {getServer, postData, removeData} from "@app/utils/utils";
import {defaultSettings} from "@app/shared/pagination";

export interface NewInventoryType {
name: string;
description?: string;
inventory?: string;
}

const inventoriesEndpoint = 'http://' + getServer() + '/api/inventories';
const inventoryEndpoint = 'http://' + getServer() + '/api/inventory';

export const listInventories = (pagination = defaultSettings) => fetch(inventoriesEndpoint, {
  headers: {
    'Content-Type': 'application/json',
  },
}).then(response => response.json());

export const fetchInventory = (id: string | number | undefined) => fetch(`${inventoryEndpoint}/${id}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then(response => response.json());

export const addInventory = (data: NewInventoryType) =>  postData(inventoriesEndpoint, data);
export const removeInventory = (inventoryId) => removeData(`${inventoryEndpoint}/${inventoryId}`);
