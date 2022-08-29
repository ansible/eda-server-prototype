import { createContext } from 'react';

const RulesTableContext = createContext<{selectedRules: string[]; setSelectedRules: ((ids: string[]) => void) | null;}> ({ selectedRules: [],
                                                                                                                                            setSelectedRules: null});

export default RulesTableContext;
