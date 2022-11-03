import { getServer, patchData, postData, removeData } from '@app/utils/utils';
import { defaultSettings } from '@app/shared/pagination';

const projectsEndpoint = 'http://' + getServer() + '/api/projects';

export interface NewProjectType {
  name: string;
  description?: string;
  scm_type?: string;
  scm_token?: string;
  url?: string;
}

export interface ProjectUpdateType {
  id: string;
  name?: string;
  description?: string;
  scm_type?: string;
  scm_token?: string;
  url?: string;
}

export const listProjects = (pagination = defaultSettings) =>
  fetch(projectsEndpoint, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then((response) => response.json());
export const fetchProject = (id: string | number | undefined) =>
  fetch(`${projectsEndpoint}/${id}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then((response) => response.json());

export const removeProject = (projectId: string | number) => removeData(`${projectsEndpoint}/${projectId}`);

export const updateProject = (project: ProjectUpdateType) =>
  patchData(`${projectsEndpoint}/${project.id}`, { name: project.name, description: project.description });

export const addProject = (projectData: NewProjectType) => postData(projectsEndpoint, projectData);
