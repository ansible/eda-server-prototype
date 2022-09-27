import {Checkbox, PageSection, Title, ToolbarGroup, ToolbarItem} from '@patternfly/react-core';
import {Link, Route, useHistory} from 'react-router-dom';
import React, {useState, useEffect, useReducer, Fragment} from 'react';
import { Button } from '@patternfly/react-core';
import {getServer} from '@app/utils/utils';
import {TopToolbar} from '../shared/top-toolbar';
import { PlusCircleIcon } from '@patternfly/react-icons';
import sharedMessages from '../messages/shared.messages';
import ProjectsTableContext from './projects-table-context';
import {TableToolbarView} from "@app/shared/table-toolbar-view";
import TableEmptyState from "@app/shared/table-empty-state";
import {useIntl} from "react-intl";
import {defaultSettings} from "@app/shared/pagination";
import {NewProject} from "@app/NewProject/NewProject";
import {EditProject} from "@app/EditProject/EditProject";
import {createRows} from "@app/Projects/projects-table-helpers";
import {AnyObject} from "@app/shared/types/common-types";
import {cellWidth} from "@patternfly/react-table";
import {RemoveProject} from "@app/RemoveProject/RemoveProject";

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
    transforms: [cellWidth(10 )]
  },
  {
    title: intl.formatMessage(sharedMessages.name)
  },
  {
    title: intl.formatMessage(sharedMessages.status)
  },
  {
    title: intl.formatMessage(sharedMessages.type)
  },
  {
    title: intl.formatMessage(sharedMessages.revision)
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
  removeModalOpen: false,
  rows: []
});

const areSelectedAll = (rows: AnyObject[] = [], selected) =>
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
}).then(response => response.json());

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

  const setSelectedProjects = (ids: string[]) =>
    stateDispatch({type: 'select', payload: ids});

  const handlePagination = (pagination) => {
    stateDispatch({type: 'setFetching', payload: true});
    return fetchProjects(pagination).then(data => { setProjects(data); stateDispatch({type: 'setRows', payload: createRows(projects)});})
      .then(() => {stateDispatch({type: 'setFetching', payload: false});})
      .catch(() => stateDispatch({type: 'setFetching', payload: false}));
  };

  useEffect(() => {
    handlePagination(defaultSettings);
  }, []);

  useEffect(() => {
    stateDispatch({type: 'setRows', payload: createRows(projects)});
  }, [projects]);

  const clearFilters = () => {
    stateDispatch({type: 'clearFilters'});
    return handlePagination(meta);
  };

  const handleFilterChange = (value) => {
    !value || value === ''
      ? clearFilters()
      : stateDispatch({type: 'setFilterValue', payload: value});
  };

   const routes = () => <Fragment>
    <Route
      exact
      path={'/projects/new-project'}
      render={(props: AnyObject) => (
        <NewProject {...props} />
      )}
    />
    <Route exact path="/projects/edit-project/:id" render={ (props: AnyObject) => <EditProject {...props} /> }/>
    <Route exact path="/projects/remove/:id"
           render={ props => <RemoveProject { ...props }
                                             fetchData={ handlePagination }
                                             setSelectedProjects={setSelectedProjects } /> }/>
    <Route exact path="/projects/remove"
           render={ props => <RemoveProject { ...props }
                                             ids={ selectedProjects }
                                             fetchData={ handlePagination }
                                             setSelectedProjects={ setSelectedProjects } /> }/>
  </Fragment>;


  const actionResolver = () => [
    {
      title: intl.formatMessage(sharedMessages.edit),
      component: 'button',
      onClick: (_event, _rowId, project) =>
        history.push({
          pathname: `/edit-project/${project.id}`
        })
    },
    {
      title: intl.formatMessage(sharedMessages.delete),
      component: 'button',
      onClick: (_event, _rowId, project) =>
        history.push({
          pathname: `/projects/remove/${project.id}`
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
            {intl.formatMessage(sharedMessages.addProject)}
          </Button>
        </Link>
      </ToolbarItem>
      <ToolbarItem>
        <Link
          id="remove-multiple-projects"
          className={anyProjectsSelected ? '' : 'disabled-link'}
          to={{pathname: '/projects/remove-projects'}}
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
        <PageSection page-type={'projects-list'} id={'projects_list'}>
          <TableToolbarView
            ouiaId={'projects-table'}
            rows={rows}
            setLimit={setLimit}
            setOffset={setOffset}
            columns={columns(intl, selectedAll, selectAllFunction)}
            fetchData={handlePagination}
            routes={routes}
            actionResolver={actionResolver}
            plural={intl.formatMessage(sharedMessages.projects)}
            singular={intl.formatMessage(sharedMessages.project)}
            toolbarButtons={toolbarButtons}
            isLoading={isFetching || isFiltering}
            onFilterChange={handleFilterChange}
            renderEmptyState={() => (
              <TableEmptyState
                title={intl.formatMessage(sharedMessages.noprojects_description)}
                Icon={PlusCircleIcon}
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
                    ? intl.formatMessage(sharedMessages.noprojects_action)
                    : intl.formatMessage(
                    sharedMessages.clearAllFiltersDescription
                    )
                }
              />
            )}
          />
        </PageSection>
      </ProjectsTableContext.Provider>
    </Fragment>
  );
}
export { Projects };
