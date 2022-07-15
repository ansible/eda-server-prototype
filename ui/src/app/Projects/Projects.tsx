import {Checkbox, PageHeader, PageSection, Title, ToolbarGroup, ToolbarItem} from '@patternfly/react-core';
import {Link, Route, useHistory} from 'react-router-dom';
import React, {useState, useEffect, useReducer, Fragment} from 'react';
import { Button } from '@patternfly/react-core';
import {getServer} from '@app/utils/utils';
import {TopToolbar} from '../shared/top-toolbar';
import { SearchIcon, PlusCircleIcon } from '@patternfly/react-icons';
import sharedMessages from '../messages/shared.messages';
import {cellWidth} from "@patternfly/react-table";
import ProjectsTableContext from './projects-table-context';
import {TableToolbarView} from "@app/shared/table-toolbar-view";
import TableEmptyState from "@app/shared/table-empty-state";
import isEmpty from 'lodash/isEmpty';
import {useIntl} from "react-intl";
import {defaultSettings} from "@app/shared/pagination";
import {NewProject} from "@app/NewProject/NewProject";
import {createRows} from "@app/Projects/projects-table-helpers";

interface ProjectType {
  id: string;
  git_hash?: string;
  url: string;
}

const endpoint = 'http://' + getServer() + '/api/projects/';

const columns = (intl, selectedAll, selectAll) => [
  {
    title: (
      <Checkbox onChange={selectAll} isChecked={selectedAll} id="select-all" />
    ),
    transforms: [cellWidth(1)]
  },
  {
    title: intl.formatMessage(sharedMessages.url)
  }
];

const prepareChips = (filterValue, intl) =>
  filterValue
    ? [
      {
        category: intl.formatMessage(sharedMessages.url),
        key: 'url',
        chips: [{ name: filterValue, value: filterValue }]
      }
    ]
    : [];

const initialState = (filterValue = '') => ({
  filterValue,
  isFetching: true,
  isFiltering: false,
  selectedProjects: [],
  selectedAll: false,
  rows: []
});

const areSelectedAll = (rows = [], selected) =>
  rows.every((row) => selected.includes(row.id));

const unique = (value, index, self) => self.indexOf(value) === index;

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const projectsListState = (state, action) => {
  switch (action.type) {
    case 'setRows':
      return {
        ...state,
        rows: action.payload,
        selectedAll: areSelectedAll(action.payload, state.selectedProjects)
      };
    case 'setFetching':
      return {
        ...state,
        isFetching: action.payload
      };
    case 'setFilterValue':
      return { ...state, filterValue: action.payload };
    case 'select':
      return {
        ...state,
        selectedAll: false,
        selectedProjects: state.selectedProjects.includes(action.payload)
          ? state.selectedProjects.filter((id) => id !== action.payload)
          : [...state.selectedProjects, action.payload]
      };
    case 'selectAll':
      return {
        ...state,
        selectedProjects: [
          ...state.selectedProjects,
          ...action.payload
        ].filter(unique),
        selectedAll: true
      };
    case 'unselectAll':
      return {
        ...state,
        selectedProjects: state.selectedProjects.filter(
          (selected) => !action.payload.includes(selected)
        ),
        selectedAll: false
      };
    case 'resetSelected':
      return {
        ...state,
        selectedProjects: [],
        selectedAll: false
      };
    case 'setFilteringFlag':
      return {
        ...state,
        isFiltering: action.payload
      };
    case 'clearFilters':
      return { ...state, filterValue: '', isFetching: true };
    default:
      return state;
  }
};

const fetchProjects = (pagination = defaultSettings) => fetch(endpoint, {
  headers: {
    'Content-Type': 'application/json',
  },
});

const Projects: React.FunctionComponent = () => {
  const intl = useIntl();
  const history = useHistory();
  const [projects, setProjects] = useState<ProjectType[]>([]);
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);

  const data = projects;
  const meta = {count: projects?.length || 0, limit, offset};
  const [
    {
      filterValue,
      isFetching,
      isFiltering,
      selectedProjects,
      selectedAll,
      rows
    },
    stateDispatch
  ] = useReducer(projectsListState, initialState());

  const setSelectedProjects = (id) =>
    stateDispatch({type: 'select', payload: id});

  const updateProjects = (pagination) => {
    stateDispatch({type: 'setFetching', payload: true});
    return fetchProjects(pagination)
      .then(() => stateDispatch({type: 'setFetching', payload: false}))
      .catch(() => stateDispatch({type: 'setFetching', payload: false}));
  };

  useEffect(() => {
    fetchProjects().then(response => response.json())
      .then(data => setProjects(data));
  }, []);
  useEffect(() => {
    updateProjects(defaultSettings);
  }, []);

  useEffect(() => {
    stateDispatch({type: 'setRows', payload: createRows(projects)});
  }, [projects]);

  const clearFilters = () => {
    stateDispatch({type: 'clearFilters'});
    return updateProjects(meta);
  };

  const handleFilterChange = (value) => {
    !value || value === ''
      ? clearFilters()
      : stateDispatch({type: 'setFilterValue', payload: value});
  };

  const routes = () => (
    <Fragment>
      <Route
        exact
        path={'/new-project'}
        render={(props) => (
          <NewProject {...props} />
        )}
      />
    </Fragment>
  );

  const actionResolver = () => [
    {
      title: intl.formatMessage(sharedMessages.delete),
      component: 'button',
      onClick: (_event, _rowId, project) =>
        history.push({
          pathname: '/remove-project',
          search: `?project=${project.id}`
        })
    }
  ];

  const selectAllFunction = () =>
    selectedAll
      ? stateDispatch({type: 'unselectAll', payload: data.map((wf) => wf.id)})
      : stateDispatch({type: 'selectAll', payload: data.map((wf) => wf.id)});

  const anyProjectsSelected = selectedProjects.length > 0;

  const toolbarButtons = () => (
    <ToolbarGroup className={`pf-u-pl-lg top-toolbar`}>
      <ToolbarItem>
        <Link
          id="add-project-link"
          to={{pathname: '/new-project'}}
        >
          <Button
            ouiaId={'add-project-link'}
            variant="primary"
            aria-label={intl.formatMessage(sharedMessages.add)}
          >
            {intl.formatMessage(sharedMessages.add)}
          </Button>
        </Link>
      </ToolbarItem>
      <ToolbarItem>
        <Link
          id="remove-multiple-projects"
          className={anyProjectsSelected ? '' : 'disabled-link'}
          to={{pathname: '/remove-projects'}}
        >
          <Button
            variant="secondary"
            isDisabled={!anyProjectsSelected}
            aria-label={intl.formatMessage(
              sharedMessages.deleteProjectTitle
            )}
          >
            {intl.formatMessage(sharedMessages.delete)}
          </Button>
        </Link>
      </ToolbarItem>
    </ToolbarGroup>
  );

  return (
    <Fragment>
      <TopToolbar>
        <Title headingLevel={"h2"}>Projects</Title>
      </TopToolbar>
      <ProjectsTableContext.Provider
        value={{
          selectedProjects,
          setSelectedProjects
        }}
      >
        <TableToolbarView
          ouiaId={'projects-table'}
          rows={rows}
          columns={columns(intl, selectedAll, selectAllFunction)}
          fetchData={updateProjects}
          routes={routes}
          actionResolver={actionResolver}
          titlePlural={intl.formatMessage(sharedMessages.projects)}
          titleSingular={intl.formatMessage(sharedMessages.project)}
          toolbarButtons={toolbarButtons}
          isLoading={isFetching || isFiltering}
          renderEmptyState={() => (
            <TableEmptyState
              title={
                filterValue === ''
                  ? intl.formatMessage(sharedMessages.noprojects)
                  : intl.formatMessage(sharedMessages.noResultsFound)
              }
              icon={isEmpty(filterValue) ? PlusCircleIcon : SearchIcon}
              PrimaryAction={() =>
                filterValue !== '' ? (
                  <Button onClick={() => clearFilters()} variant="link">
                    {intl.formatMessage(sharedMessages.clearAllFilters)}
                  </Button>
                ) : (
                  <Link
                    id="create-project-link"
                    to={{pathname: '/new-project'}}
                  >
                    <Button
                      ouiaId={'create-project-link'}
                      variant="primary"
                      aria-label={intl.formatMessage(
                        sharedMessages.addProject
                      )}
                    >
                      {intl.formatMessage(sharedMessages.addProject)}
                    </Button>
                  </Link>
                )
              }
              description={
                filterValue === ''
                  ? intl.formatMessage(sharedMessages.noprojects)
                  : intl.formatMessage(
                  sharedMessages.clearAllFiltersDescription
                  )
              }
              isSearch={!isEmpty(filterValue)}
            />
          )}
          activeFiltersConfig={{
            filters: prepareChips(filterValue, intl),
            onDelete: () => handleFilterChange('')
          }}
        />
      </ProjectsTableContext.Provider>
    </Fragment>
  );
}
export { Projects };
