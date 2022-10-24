import {PageSection, Title, ToolbarGroup, ToolbarItem} from '@patternfly/react-core';
import {Link, Route, useHistory} from 'react-router-dom';
import React, {useState, useEffect, useReducer, Fragment} from 'react';
import { Button } from '@patternfly/react-core';
import {getServer} from '@app/utils/utils';
import {TopToolbar} from "@app/shared/top-toolbar";
import { PlusCircleIcon } from '@patternfly/react-icons';
import sharedMessages from '../messages/shared.messages';
import {cellWidth} from "@patternfly/react-table";
import JobsTableContext from './jobs-table-context';
import {TableToolbarView} from "@app/shared/table-toolbar-view";
import TableEmptyState from "@app/shared/table-empty-state";
import {useIntl} from "react-intl";
import {defaultSettings} from "@app/shared/pagination";
import {NewJob} from "@app/NewJob/NewJob";
import {createRows} from "@app/Jobs/jobs-table-helpers";
import {RemoveJob} from "@app/RemoveJob/RemoveJob";
import {listJobs} from "@app/API/Job";

interface JobType {
  id: string;
  name?: string;
}

interface JobRowType {
  id: string;
  name?: string;
  isChecked: boolean
}

const columns = (intl) => [
  {
    title: (''),
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

const areSelectedAll = (rows:JobRowType[] = [], selected) =>
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

const Jobs: React.FunctionComponent = () => {
  const intl = useIntl();
  const history = useHistory();
  const [jobs, setJobs] = useState<JobType[]>([]);
  const [newJob, setNewJob] = useState<JobType>({id:''});
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

  const setSelectedJobs = (id: string) =>
    stateDispatch({type: 'select', payload: id});

  const handlePagination = (pagination) => {
    stateDispatch({type: 'setFetching', payload: true});
    return listJobs(pagination).then(data => { setJobs(data); stateDispatch({type: 'setRows', payload: createRows(jobs)});})
      .then(() => {stateDispatch({type: 'setFetching', payload: false});})
      .catch(() => stateDispatch({type: 'setFetching', payload: false}));
  };

  useEffect(() => {
    handlePagination(defaultSettings);
  }, []);

  useEffect(() => {
    stateDispatch({type: 'setRows', payload: createRows(jobs)});
  }, [jobs]);


  const [update_client, setUpdateClient] = useState<WebSocket|unknown>({});
  useEffect(() => {
    const uc = new WebSocket('ws://' + getServer() + '/api/ws-jobs/');
    setUpdateClient(uc);
    uc.onopen = () => {
      console.log('Update client connected');
    };
    uc.onmessage = (message) => {
      console.log('update: ' + message.data);
      const [messageType, data] = JSON.parse(message.data);
      if (messageType === 'Job') {
        setNewJob(data);
      }
    }
  }, []);

  const clearFilters = () => {
    stateDispatch({type: 'clearFilters'});
    return handlePagination(meta);
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
        path={'/new-job'}>
        <NewJob/>
      </Route>
      <Route exact path="/jobs/remove"
             render={ props => <RemoveJob { ...props }
                                              ids={ selectedJobs }
                                              fetchData={ handlePagination }
                                              resetSelectedJobs={() =>
                                                stateDispatch({ type: 'resetSelected' })
                                              }/>}/>
      <Route exact path="/jobs/remove/:id"
             render={ props => <RemoveJob { ...props }
                                              fetchData={ handlePagination }
             /> }/>
    </Fragment>
  );

  const actionResolver = () => [
    {
      title: intl.formatMessage(sharedMessages.delete),
      component: 'button',
      onClick: (_event, _rowId, job) =>
        history.push({
          pathname: `/jobs/remove/${job.id}`
        })
    }
  ];

  const selectAllFunction = () =>
      stateDispatch({type: 'selectAll', payload: data.map(( item) =>  item.id)});

  const unselectAllFunction = () =>
    stateDispatch({type: 'unselectAll', payload: data.map(( item) =>  item.id)});

  const anyJobsSelected = selectedJobs.length > 0;

  const bulkSelectProps = React.useMemo(() => {
    return {
      count: selectedJobs.length || 0,
      items: [
        {
          title: 'Select none (0)',
          onClick: unselectAllFunction
        },
        {
          title: `Select all (${jobs.length || 0})`,
          onClick: selectAllFunction
        }
      ],
      checked: selectedJobs.length === jobs.length,
      onSelect: (isChecked: boolean) => isChecked ? selectAllFunction() : unselectAllFunction()
    };
  }, [ selectedJobs.length, jobs.length ]);

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
          to={{pathname: '/jobs/remove'}}
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
            setLimit={setLimit}
            setOffset={setOffset}
            columns={columns(intl)}
            bulkSelect={bulkSelectProps}
            fetchData={handlePagination}
            routes={routes}
            actionResolver={actionResolver}
            plural={intl.formatMessage(sharedMessages.jobs)}
            singular={intl.formatMessage(sharedMessages.job)}
            toolbarButtons={toolbarButtons}
            isLoading={isFetching || isFiltering}
            onFilterChange={handleFilterChange}
            renderEmptyState={() => (
              <TableEmptyState
                title={intl.formatMessage(sharedMessages.nojobs_description)}
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
                    ? intl.formatMessage(sharedMessages.nojobs_action)
                    : intl.formatMessage(
                    sharedMessages.clearAllFiltersDescription
                    )
                }
              />
            )}
          />
        </PageSection>
      </JobsTableContext.Provider>
    </Fragment>
  );
}
export { Jobs };
