import { createContext } from 'react';

const InventoriesTableContext = createContext<{
  selectedInventories: string[];
  setSelectedInventories: ((ids: string) => void) | null;
}>({ selectedInventories: [], setSelectedInventories: null });

export default InventoriesTableContext;
