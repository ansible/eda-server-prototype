import { Button, PageSection } from '@patternfly/react-core';
import React, { useEffect, useReducer, useState } from 'react';
import { TableToolbarView } from '@app/shared/table-toolbar-view';
import sharedMessages from '../messages/shared.messages';
import TableEmptyState from '@app/shared/table-empty-state';
import { useIntl } from 'react-intl';
import { defaultSettings } from '@app/shared/pagination';
import { createRows } from './actions-rule-jobs-table-helpers';
import { CubesIcon } from '@patternfly/react-icons';
import { JobType } from '@app/Job/Job';
import {listActionsRuleJobs} from '@app/API/Actions';
import { RuleType } from '@app/Rules/Rules';
import { renderActionsRuleTabs } from '@app/Actions/ActionsRule';

const columns = (intl) => [
  {
    title: intl.formatMessage(sharedMessages.name),
  },
  {
    title: intl.formatMessage(sharedMessages.status),
  },
  {
    title: intl.formatMessage(sharedMessages.lastFiredDate),
  },
];

const initialState = (filterValue = '') => ({
  filterValue,
  isFetching: false,
  isFiltering: false,
  rows: [],
});

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const jobsListState = (state, action) => {
  switch (action.type) {
    case 'setRows':
      return {
        ...state,
        rows: action.payload,
      };
    case 'setFetching':
      return {
        ...state,
        isFetching: action.payload,
      };
    case 'setFilterValue':
      return { ...state, filterValue: action.payload };
    case 'setFilteringFlag':
      return {
        ...state,
        isFiltering: action.payload,
      };
    case 'clearFilters':
      return { ...state, filterValue: '', isFetching: true };
    default:
      return state;
  }
};

const ActionsRuleJobs: React.FunctionComponent<{ rule: RuleType }> = ({ rule }) => {
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);
  const [jobs, setJobs] = useState<JobType[]>([]);

  const meta = { count: jobs?.length || 0, limit, offset };
  const [{ filterValue, isFetching, isFiltering, rows }, stateDispatch] = useReducer(jobsListState, initialState());

  const intl = useIntl();
  const updateJobs = (pagination) => {
    stateDispatch({ type: 'setFetching', payload: true });
    return listActionsRuleJobs(rule.id, pagination)
      .then((data) => {
        setJobs(data?.data);
        return stateDispatch({ type: 'setFetching', payload: false });
      })
      .catch(() => stateDispatch({ type: 'setFetching', payload: false }));
  };

  useEffect(() => {
    updateJobs(defaultSettings);
  }, []);

  useEffect(() => {
    stateDispatch({ type: 'setRows', payload: createRows(jobs, intl) });
  }, [jobs]);

  const clearFilters = () => {
    stateDispatch({ type: 'clearFilters' });
    return updateJobs(meta);
  };

  const handleFilterChange = (value) => {
    !value || value === '' ? clearFilters() : stateDispatch({ type: 'setFilterValue', payload: value });
  };

  return (
    <PageSection page-type={'actions-rule-jobs'} id={'actions-rule-jobs'}>
      {renderActionsRuleTabs(rule?.id, intl)}
      <TableToolbarView
        ouiaId={'actions-rule-jobs-table'}
        rows={rows}
        setLimit={setLimit}
        setOffset={setOffset}
        columns={columns(intl)}
        fetchData={updateJobs}
        pagination={defaultSettings}
        plural={intl.formatMessage(sharedMessages.jobs)}
        singular={intl.formatMessage(sharedMessages.job)}
        isLoading={isFetching || isFiltering}
        onFilterChange={handleFilterChange}
        renderEmptyState={() => (
          <TableEmptyState
            title={intl.formatMessage(sharedMessages.noactionsrulejobs)}
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
                ? intl.formatMessage(sharedMessages.noactionsrulejobs)
                : intl.formatMessage(sharedMessages.clearAllFiltersDescription)
            }
          />
        )}
      />
    </PageSection>
  );
};

export { ActionsRuleJobs };
