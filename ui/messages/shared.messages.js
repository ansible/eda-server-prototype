// eslint-disable-next-line @typescript-eslint/no-var-requires
const { defineMessages } = require('react-intl');

const sharedMessages = defineMessages({
  name: {
    id: 'shared.url',
    defaultMessage: 'Url'
  },
  url: {
    id: 'shared.name',
    defaultMessage: 'Name'
  },
  add: {
    id: 'shared.add',
    defaultMessage: 'Add'
  },
  delete: {
    id: 'shared.delete',
    defaultMessage: 'Delete'
  },
  filterByTitle: {
    id: 'shared.filterByTitle',
    defaultMessage: 'Filter by {title}'
  },
  noResultsFound: {
    id: 'shared.noResultsFound',
    defaultMessage: 'No results found'
  },
  noResult: {
    id: 'shared.noResult',
    defaultMessage: 'No {results}'
  },
  clearAllFilters: {
    id: 'shared.clearAllFilters',
    defaultMessage: 'Clear all filters'
  },
  clearAllFiltersDescription: {
    id: 'shared.clearAllFiltersDescription',
    defaultMessage:
      'No results match the filter criteria. Remove all filters or clear all filters to show results.'
  },
  ariaLabel: {
    id: 'shared.ariaLabel',
    defaultMessage: '{title} table'
  },
  updatedLabel: {
    id: 'shared.updatedLabel',
    defaultMessage: 'Updated'
  },
  project: {
    id: 'project.project',
    defaultMessage: 'Project'
  },
  projects: {
    id: 'project.projects',
    defaultMessage: 'Projects'
  },
  noprojects: {
    id: 'project.noprojects',
    defaultMessage: 'No projects'
  },
  addProject: {
    id: 'project.addProject',
    defaultMessage: 'Add project'
  },
  deleteProjectTitle: {
    id: 'project.deleteProject',
    defaultMessage: 'Delete project'
  }
});

export default sharedMessages;
