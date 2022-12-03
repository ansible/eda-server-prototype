import { Button, PageSection } from '@patternfly/react-core';
import React, { useEffect, useReducer, useState } from 'react';
import { TableToolbarView } from '@app/shared/table-toolbar-view';
import sharedMessages from '../messages/shared.messages';
import { cellWidth } from '@patternfly/react-table';
import TableEmptyState from '@app/shared/table-empty-state';
import { useIntl } from 'react-intl';
import { defaultSettings } from '@app/shared/pagination';
import { createRows } from './audit-hosts-table-helpers';
import { CubesIcon } from '@patternfly/react-icons';
import { renderAuditTabs } from '@app/AuditView/AuditView';
import { AuditHostType } from '@app/AuditView/AuditView';
import { listAuditHosts } from '@app/API/Audit';

const columns = (intl) => [
  {
    title: intl.formatMessage(sharedMessages.name),
    transforms: [cellWidth(40)],
  },
  {
    title: intl.formatMessage(sharedMessages.rule),
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
export const auditHostsListState = (state, action) => {
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

const AuditHosts: React.FunctionComponent = () => {
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);
  const [auditHosts, setAuditHosts] = useState<AuditHostType[]>([]);

  const meta = { count: auditHosts?.length || 0, limit, offset };

  const [{ filterValue, isFetching, isFiltering, rows }, stateDispatch] = useReducer(
    auditHostsListState,
    initialState()
  );

  const intl = useIntl();
  const updateAuditHosts = (pagination) => {
    stateDispatch({ type: 'setFetching', payload: true });
    return listAuditHosts(pagination)
      .then((data) => {
        setAuditHosts(data.data);
        return stateDispatch({ type: 'setFetching', payload: false });
      })
      .catch(() => stateDispatch({ type: 'setFetching', payload: false }));
  };

  useEffect(() => {
    stateDispatch({ type: 'setRows', payload: createRows(auditHosts) });
  }, [auditHosts]);

  useEffect(() => {
    updateAuditHosts(defaultSettings);
  }, []);

  const clearFilters = () => {
    stateDispatch({ type: 'clearFilters' });
    return updateAuditHosts(meta);
  };

  const handleFilterChange = (value) => {
    !value || value === '' ? clearFilters() : stateDispatch({ type: 'setFilterValue', payload: value });
  };

  return (
    <PageSection page-type={'activation-details'} id={'activation-details'}>
      {renderAuditTabs(intl)}
      <TableToolbarView
        ouiaId={'audit-hosts-table'}
        rows={rows}
        setLimit={setLimit}
        setOffset={setOffset}
        columns={columns(intl)}
        fetchData={updateAuditHosts}
        pagination={defaultSettings}
        plural={intl.formatMessage(sharedMessages.hosts)}
        singular={intl.formatMessage(sharedMessages.host)}
        isLoading={isFetching || isFiltering}
        onFilterChange={handleFilterChange}
        renderEmptyState={() => (
          <TableEmptyState
            title={intl.formatMessage(sharedMessages.nohostsrecentlychanged)}
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
                ? intl.formatMessage(sharedMessages.nohostsrecentlychanged)
                : intl.formatMessage(sharedMessages.clearAllFiltersDescription)
            }
          />
        )}
      />
    </PageSection>
  );
};

export { AuditHosts };
