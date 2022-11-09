import { createContext } from 'react';
import { InventorySelectType } from '@app/InventoriesSelect/InventoriesSelect';

const InventoriesSelectTableContext = createContext<{
  selectedInventory: InventorySelectType | undefined;
  setSelectedInventory: ((inventory: InventorySelectType | undefined) => void) | null;
}>({ selectedInventory: undefined, setSelectedInventory: null });

export default InventoriesSelectTableContext;
