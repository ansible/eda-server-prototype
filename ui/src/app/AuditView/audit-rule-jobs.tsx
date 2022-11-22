import { Button, PageSection } from '@patternfly/react-core';
import React, { useEffect, useReducer, useState } from 'react';
import { TableToolbarView } from '@app/shared/table-toolbar-view';
import sharedMessages from '../messages/shared.messages';
import { cellWidth } from '@patternfly/react-table';
import TableEmptyState from '@app/shared/table-empty-state';
import { useIntl } from 'react-intl';
import { defaultSettings } from '@app/shared/pagination';
import { createRows } from './audit-rule-jobs-table-helpers';
import { CubesIcon } from '@patternfly/react-icons';
import { JobType } from '@app/Job/Job';
import { listAuditRuleJobs } from '@app/API/Audit';
import {RuleType} from "@app/Rules/Rules";
import {renderAuditRuleTabs} from "@app/AuditView/AuditRule";

const columns = (intl) => [
  {
    title: intl.formatMessage(sharedMessages.jobs),
    transforms: [cellWidth(40)],
  },
  {
    title: intl.formatMessage(sharedMessages.status),
  },
  {
    title: intl.formatMessage(sharedMessages.rule),
  },
  {
    title: intl.formatMessage(sharedMessages.lastFiredDate),
  },
];

const prepareChips = (filterValue, intl) =>
  filterValue
    ? [
        {
          category: intl.formatMessage(sharedMessages.name),
          key: 'name',
          chips: [{ name: filterValue, value: filterValue }],
        },
      ]
    : [];

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

const AuditRuleJobs: React.FunctionComponent<{ rule: RuleType }> = ({ rule }) => {
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);
  const [jobs, setJobs] = useState<JobType[]>([]);

  const meta = { count: jobs?.length || 0, limit, offset };
  const [{ filterValue, isFetching, isFiltering, rows }, stateDispatch] = useReducer(jobsListState, initialState());

  const intl = useIntl();
  const updateJobs = (pagination) => {
    stateDispatch({ type: 'setFetching', payload: true });
    return listAuditRuleJobs(rule?.id, pagination)
      .then(() => stateDispatch({ type: 'setFetching', payload: false }))
      .catch(() => stateDispatch({ type: 'setFetching', payload: false }));
  };

  useEffect(() => {
    updateJobs(defaultSettings);
  }, []);

  useEffect(() => {
    stateDispatch({ type: 'setRows', payload: createRows(jobs) });
  }, [jobs]);

  const clearFilters = () => {
    stateDispatch({ type: 'clearFilters' });
    return updateJobs(meta);
  };

  const handleFilterChange = (value) => {
    !value || value === '' ? clearFilters() : stateDispatch({ type: 'setFilterValue', payload: value });
  };

  return (
    <PageSection page-type={'audit-rule-jobs'} id={'audit-rule-jobs'}>
      {renderAuditRuleTabs(rule?.id, intl)}
      <TableToolbarView
        ouiaId={'audit-rule-jobs-table'}
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
            title={intl.formatMessage(sharedMessages.noauditrulejobs)}
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
                ? intl.formatMessage(sharedMessages.noauditrulejobs)
                : intl.formatMessage(sharedMessages.clearAllFiltersDescription)
            }
          />
        )}
      />
    </PageSection>
  );
};

export { AuditRuleJobs };
