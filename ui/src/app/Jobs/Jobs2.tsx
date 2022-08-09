import {Checkbox, PageSection, Title, ToolbarGroup, ToolbarItem} from '@patternfly/react-core';
import {Link, Route, useHistory} from 'react-router-dom';
import React, {useState, useEffect, useReducer, Fragment} from 'react';
import { Button } from '@patternfly/react-core';
import {getServer} from '@app/utils/utils';
import {TopToolbar} from '../shared/top-toolbar';
import { PlusCircleIcon } from '@patternfly/react-icons';
import sharedMessages from '../messages/shared.messages';
import {cellWidth} from "@patternfly/react-table";
import JobsTableContext from './jobs-table-context';
import {TableToolbarView} from "@app/shared/table-toolbar-view";
import TableEmptyState from "@app/shared/table-empty-state";
import isEmpty from 'lodash/isEmpty';
import {useIntl} from "react-intl";
import {defaultSettings} from "@app/shared/pagination";
import {NewJob} from "@app/NewJob/NewJob";
import {createRows} from "@app/Jobs/jobs-table-helpers";

interface JobType {
  id: string;
  git_hash?: string;
  name: string;
}

const endpoint = 'http://' + getServer() + '/api/job_instances/';

const columns = (intl, selectedAll, selectAll) => [
  {
    title: (
      <Checkbox onChange={selectAll} isChecked={selectedAll} id="select-all" />
    ),
    transforms: [cellWidth(10 )]
  },
  {
  title: (intl.formatMessage(sharedMessages.name)),
    transforms: [cellWidth(80 )]
  }
];

const prepareChips = (filterValue, intl) =>
  filterValue
    ? [
      {
        category: intl.formatMessage(sharedMessages.name),
        key: 'name',
        chips: [{ name: filterValue, value: filterValue }]
      }
    ]
    : [];

const initialState = (filterValue = '') => ({
  filterValue,
  isFetching: true,
  isFiltering: false,
  selectedJobs: [],
  selectedAll: false,
  rows: []
});

const areSelectedAll = (rows = [], selected) =>
  rows.every((row) => selected.includes(row.id));

const unique = (value, index, self) => self.indexOf(value) === index;

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const jobsListState = (state, action) => {
  switch (action.type) {
    case 'setRows':
      return {
        ...state,
        rows: action.payload,
        selectedAll: areSelectedAll(action.payload, state.selectedJobs)
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
        selectedJobs: state.selectedJobs.includes(action.payload)
          ? state.selectedJobs.filter((id) => id !== action.payload)
          : [...state.selectedJobs, action.payload]
      };
    case 'selectAll':
      return {
        ...state,
        selectedJobs: [
          ...state.selectedJobs,
          ...action.payload
        ].filter(unique),
        selectedAll: true
      };
    case 'unselectAll':
      return {
        ...state,
        selectedJobs: state.selectedJobs.filter(
          (selected) => !action.payload.includes(selected)
        ),
        selectedAll: false
      };
    case 'resetSelected':
      return {
        ...state,
        selectedJobs: [],
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

const fetchJobs = (pagination = defaultSettings) => fetch(endpoint, {
  headers: {
    'Content-Type': 'application/json',
  },
});

const Jobs: React.FunctionComponent = () => {
  const intl = useIntl();
  const history = useHistory();
  const [jobs, setJobs] = useState<JobType[]>([]);
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);

  const data = jobs;
  const meta = {count: jobs?.length || 0, limit, offset};
  const [
    {
      filterValue,
      isFetching,
      isFiltering,
      selectedJobs,
      selectedAll,
      rows
    },
    stateDispatch
  ] = useReducer(jobsListState, initialState());

  const setSelectedJobs = (id) =>
    stateDispatch({type: 'select', payload: id});

  const updateJobs = (pagination) => {
    stateDispatch({type: 'setFetching', payload: true});
    return fetchJobs(pagination)
      .then(() => stateDispatch({type: 'setFetching', payload: false}))
      .catch(() => stateDispatch({type: 'setFetching', payload: false}));
  };

  useEffect(() => {
    fetchJobs().then(response => response.json())
      .then(data => { setJobs(data); stateDispatch({type: 'setRows', payload: createRows(jobs)});});
  }, []);

  useEffect(() => {
    updateJobs(defaultSettings);
  }, []);

  useEffect(() => {
    stateDispatch({type: 'setRows', payload: createRows(jobs)});
  }, [jobs]);

  const clearFilters = () => {
    stateDispatch({type: 'clearFilters'});
    return updateJobs(meta);
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
        path={'/new-job'}
        render={(props) => (
          <NewJob {...props} />
        )}
      />
    </Fragment>
  );

  const actionResolver = () => [
    {
      title: intl.formatMessage(sharedMessages.delete),
      component: 'button',
      onClick: (_event, _rowId, job) =>
        history.push({
          pathname: '/remove-job',
          search: `?job=${job.id}`
        })
    }
  ];

  const selectAllFunction = () =>
    selectedAll
      ? stateDispatch({type: 'unselectAll', payload: data.map((wf) => wf.id)})
      : stateDispatch({type: 'selectAll', payload: data.map((wf) => wf.id)});

  const anyJobsSelected = selectedJobs.length > 0;

  const toolbarButtons = () => (
    <ToolbarGroup className={`pf-u-pl-lg top-toolbar`}>
      <ToolbarItem>
        <Link
          id="add-job-link"
          to={{pathname: '/new-job'}}
        >
          <Button
            ouiaId={'add-job-link'}
            variant="primary"
            aria-label={intl.formatMessage(sharedMessages.add)}
          >
            {intl.formatMessage(sharedMessages.add)}
          </Button>
        </Link>
      </ToolbarItem>
      <ToolbarItem>
        <Link
          id="remove-multiple-jobs"
          className={anyJobsSelected ? '' : 'disabled-link'}
          to={{pathname: '/remove-jobs'}}
        >
          <Button
            variant="secondary"
            isDisabled={!anyJobsSelected}
            aria-label={intl.formatMessage(
              sharedMessages.deleteJobTitle
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
        <Title headingLevel={"h2"}>Jobs</Title>
      </TopToolbar>
      <JobsTableContext.Provider
        value={{
          selectedJobs,
          setSelectedJobs
        }}
      >
        <PageSection>
          <TableToolbarView
            ouiaId={'jobs-table'}
            rows={rows}
            columns={columns(intl, selectedAll, selectAllFunction)}
            fetchData={updateJobs}
            routes={routes}
            actionResolver={actionResolver}
            titlePlural={intl.formatMessage(sharedMessages.jobs)}
            titleSingular={intl.formatMessage(sharedMessages.job)}
            toolbarButtons={toolbarButtons}
            isLoading={isFetching || isFiltering}
            renderEmptyState={() => (
              <TableEmptyState
                title={intl.formatMessage(sharedMessages.nojobs)}
                Icon={PlusCircleIcon}
                PrimaryAction={() =>
                  filterValue !== '' ? (
                    <Button onClick={() => clearFilters()} variant="link">
                      {intl.formatMessage(sharedMessages.clearAllFilters)}
                    </Button>
                  ) : (
                    <Link
                      id="create-job-link"
                      to={{pathname: '/new-job'}}
                    >
                      <Button
                        ouiaId={'create-job-link'}
                        variant="primary"
                        aria-label={intl.formatMessage(
                          sharedMessages.addJob
                        )}
                      >
                        {intl.formatMessage(sharedMessages.addJob)}
                      </Button>
                    </Link>
                  )
                }
                description={
                  filterValue === ''
                    ? intl.formatMessage(sharedMessages.nojobs)
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
        </PageSection>
      </JobsTableContext.Provider>
    </Fragment>
  );
}
export { Jobs };
