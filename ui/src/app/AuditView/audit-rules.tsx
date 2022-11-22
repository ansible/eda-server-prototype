import { Button, PageSection } from '@patternfly/react-core';
import React, { useEffect, useReducer, useState } from 'react';
import { TableToolbarView } from '@app/shared/table-toolbar-view';
import sharedMessages from '../messages/shared.messages';
import { cellWidth } from '@patternfly/react-table';
import TableEmptyState from '@app/shared/table-empty-state';
import { useIntl } from 'react-intl';
import { defaultSettings } from '@app/shared/pagination';
import { createRows } from './audit-rules-table-helpers';
import { CubesIcon } from '@patternfly/react-icons';
import { renderAuditTabs } from '@app/AuditView/AuditView';
import { AuditRuleType } from '@app/AuditView/AuditView';
import { listAuditRules } from '@app/API/Audit';

const columns = (intl) => [
  {
    title: intl.formatMessage(sharedMessages.name),
  },
  {
    title: intl.formatMessage(sharedMessages.job),
  },
  {
    title: intl.formatMessage(sharedMessages.status),
  },
  {
    title: intl.formatMessage(sharedMessages.ruleset),
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
export const auditRulesListState = (state, action) => {
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

const AuditRules: React.FunctionComponent = () => {
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);
  const [auditRules, setAuditRules] = useState<AuditRuleType[]>([]);

  const meta = { count: auditRules?.length || 0, limit, offset };

  const [{ filterValue, isFetching, isFiltering, rows }, stateDispatch] = useReducer(
    auditRulesListState,
    initialState()
  );

  const intl = useIntl();
  const updateAuditRules = (pagination) => {
    stateDispatch({ type: 'setFetching', payload: true });
    return listAuditRules(pagination)
      .then((data) => {
        setAuditRules(data.data);
        return stateDispatch({ type: 'setFetching', payload: false });
      })
      .catch(() => stateDispatch({ type: 'setFetching', payload: false }));
  };

  useEffect(() => {
    updateAuditRules(defaultSettings);
  }, []);

  useEffect(() => {
    stateDispatch({ type: 'setRows', payload: createRows(auditRules) });
  }, [auditRules]);

  const clearFilters = () => {
    stateDispatch({ type: 'clearFilters' });
    return updateAuditRules(meta);
  };

  const handleFilterChange = (value) => {
    !value || value === '' ? clearFilters() : stateDispatch({ type: 'setFilterValue', payload: value });
  };

  return (
    <PageSection page-type={'activation-details'} id={'activation-details'}>
      {renderAuditTabs(intl)}
      <TableToolbarView
        ouiaId={'audit-rules-table'}
        rows={rows}
        setLimit={setLimit}
        setOffset={setOffset}
        columns={columns(intl)}
        fetchData={updateAuditRules}
        pagination={defaultSettings}
        plural={intl.formatMessage(sharedMessages.rules)}
        singular={intl.formatMessage(sharedMessages.rule)}
        isLoading={isFetching || isFiltering}
        onFilterChange={handleFilterChange}
        renderEmptyState={() => (
          <TableEmptyState
            title={intl.formatMessage(sharedMessages.norulesrecentlyfired)}
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
                ? intl.formatMessage(sharedMessages.norulesrecentlyfired)
                : intl.formatMessage(sharedMessages.clearAllFiltersDescription)
            }
          />
        )}
      />
    </PageSection>
  );
};

export { AuditRules };
