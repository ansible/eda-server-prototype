import {Button, PageSection} from '@patternfly/react-core';
import {useHistory} from 'react-router-dom';
import React, {useEffect, useReducer, useState} from 'react';
import {fetchActivationJobs, renderActivationTabs} from "@app/Activation/Activation";
import {TableToolbarView} from "@app/shared/table-toolbar-view";
import sharedMessages from "../messages/shared.messages";
import {cellWidth} from "@patternfly/react-table";
import TableEmptyState from "@app/shared/table-empty-state";
import isEmpty from 'lodash/isEmpty';
import {useIntl} from "react-intl";
import {defaultSettings} from "@app/shared/pagination";
import {createRows} from "./jobs-table-helpers";
import {CubesIcon} from "@patternfly/react-icons";

const columns = (intl) => [
  {
    title: (intl.formatMessage(sharedMessages.jobs)),
    transforms: [cellWidth(40 )]
  },
  {
    title: (intl.formatMessage(sharedMessages.status))
  },
  {
    title: (intl.formatMessage(sharedMessages.rule))
  },
  {
    title: (intl.formatMessage(sharedMessages.lastFiredDate))
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
  isFetching: false,
  isFiltering: false,
  rows: []
});

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const jobsListState = (state, action) => {
  switch (action.type) {
    case 'setRows':
      return {
        ...state,
        rows: action.payload
      };
    case 'setFetching':
      return {
        ...state,
        isFetching: action.payload
      };
    case 'setFilterValue':
      return { ...state, filterValue: action.payload };
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

const ActivationJobs: React.FunctionComponent = ({activation, jobs}) => {
  const intl = useIntl();
  const history = useHistory();
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);

  const data = jobs;
  const meta = {count: jobs?.length || 0, limit, offset};
  const [
    {
      filterValue,
      isFetching,
      isFiltering,
      rows
    },
    stateDispatch
  ] = useReducer(jobsListState, initialState());

  const updateJobs = (pagination) => {
    stateDispatch({type: 'setFetching', payload: true});
    return fetchActivationJobs(activation?.id, pagination)
      .then(() => stateDispatch({type: 'setFetching', payload: false}))
      .catch(() => stateDispatch({type: 'setFetching', payload: false}));
  };

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

  return (
    <PageSection page-type={'activation-details'} id={'activation-details'}>
      { renderActivationTabs(activation?.id) }
      <TableToolbarView
        ouiaId={'activations-table'}
        rows={rows}
        columns={columns(intl)}
        fetchData={updateJobs}
        titlePlural={intl.formatMessage(sharedMessages.jobs)}
        titleSingular={intl.formatMessage(sharedMessages.job)}
        isLoading={isFetching || isFiltering}
        renderEmptyState={() => (
          <TableEmptyState
            title={intl.formatMessage(sharedMessages.nojobs)}
            Icon={CubesIcon}
            PrimaryAction={() =>
              filterValue !== '' ? (
                <Button onClick={() => clearFilters()} variant="link">
                  {intl.formatMessage(sharedMessages.clearAllFilters)}
                </Button>
              ) : null
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
  );
}

export { ActivationJobs };
