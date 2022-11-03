import { createContext } from 'react';

interface IJobsTableContext {
  selectedJobs: string[];
  setSelectedJobs?: (string) => void;
}

const defaultState = {
  selectedJobs: [],
};

const JobsTableContext = createContext<IJobsTableContext>({ selectedJobs: [] });

export default JobsTableContext;
