import { defaultSettings } from '@app/shared/pagination';
import { AxiosResponse } from 'axios';
import { getAxiosInstance } from '@app/API/baseApi';

const projectsEndpoint = '/api/projects';

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

export const listProjects = (pagination = defaultSettings): Promise<AxiosResponse> =>
  getAxiosInstance().get(projectsEndpoint);

export const fetchProject = (id: string | number | undefined): Promise<AxiosResponse> =>
  getAxiosInstance().get(`${projectsEndpoint}/${id}`);

export const removeProject = (projectId: string | number): Promise<AxiosResponse> =>
  getAxiosInstance().delete(`${projectsEndpoint}/${projectId}`);

export const updateProject = (project: ProjectUpdateType): Promise<AxiosResponse> =>
  getAxiosInstance().patch(`${projectsEndpoint}/${project.id}`, {
    name: project.name,
    description: project.description,
  });

export const addProject = (projectData: NewProjectType): Promise<AxiosResponse> =>
  getAxiosInstance().post(projectsEndpoint, projectData);
