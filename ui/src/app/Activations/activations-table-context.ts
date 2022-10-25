import { createContext } from 'react';

const ActivationsTableContext = createContext<{
  selectedActivations: string[];
  setSelectedActivations: ((ids: string[]) => void) | null;
}>({ selectedActivations: [], setSelectedActivations: null });

export default ActivationsTableContext;
