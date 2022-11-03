import { createContext } from 'react';

interface IProjectsTableContext {
  selectedProjects: string[];
  setSelectedProjects?: (string) => void;
}

const defaultState = {
  selectedProjects: [],
};

const ProjectsTableContext = createContext<{
  selectedProjects: string[];
  setSelectedProjects: ((ids: string[]) => void) | null;
}>({ selectedProjects: [], setSelectedProjects: null });

export default ProjectsTableContext;
