import { createContext } from 'react';

const ProjectsTableContext = createContext<{selectedProjects: string[]; setSelectedProjects: ((ids: string[]) => void) | null;}> ({ selectedProjects: [],
                                                                                                                                            setSelectedProjects: null});

export default ProjectsTableContext;
