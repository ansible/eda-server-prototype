import { Button, PageSection } from '@patternfly/react-core';
import React, { useEffect, useReducer, useState } from 'react';
import { TableToolbarView } from '@app/shared/table-toolbar-view';
import sharedMessages from '../messages/shared.messages';
import TableEmptyState from '@app/shared/table-empty-state';
import { useIntl } from 'react-intl';
import { defaultSettings } from '@app/shared/pagination';
import { createRows } from './actions-rule-hosts-table-helpers';
import { CubesIcon } from '@patternfly/react-icons';
import {listActionsRuleHosts} from '@app/API/Actions';
import { RuleType } from '@app/Rules/Rules';
import { renderActionsRuleTabs } from '@app/Actions/ActionsRule';

export interface HostType {
  name: string;
  status?: string;
}

const columns = (intl) => [
  {
    title: intl.formatMessage(sharedMessages.name),
  },
  {
    title: intl.formatMessage(sharedMessages.status),
  },
];

const initialState = (filterValue = '') => ({
  filterValue,
  isFetching: false,
  isFiltering: false,
  rows: [],
});

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const hostsListState = (state, action) => {
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

const ActionsRuleHosts: React.FunctionComponent<{ rule: RuleType }> = ({ rule }) => {
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);
  const [hosts, setHosts] = useState<HostType[]>([]);

  const meta = { count: hosts?.length || 0, limit, offset };
  const [{ filterValue, isFetching, isFiltering, rows }, stateDispatch] = useReducer(hostsListState, initialState());

  const intl = useIntl();
  const updateHosts = (pagination) => {
    stateDispatch({ type: 'setFetching', payload: true });
    return listActionsRuleHosts(rule.id, pagination)
      .then((data) => {
        setHosts(data?.data);
        return stateDispatch({ type: 'setFetching', payload: false });
      })
      .catch(() => stateDispatch({ type: 'setFetching', payload: false }));
  };

  useEffect(() => {
    updateHosts(defaultSettings);
  }, []);

  useEffect(() => {
    stateDispatch({ type: 'setRows', payload: createRows(hosts, intl) });
  }, [hosts]);

  const clearFilters = () => {
    stateDispatch({ type: 'clearFilters' });
    return updateHosts(meta);
  };

  const handleFilterChange = (value) => {
    !value || value === '' ? clearFilters() : stateDispatch({ type: 'setFilterValue', payload: value });
  };
  return (
    <PageSection page-type={'actions-rule-hosts'} id={'actions-rule-hosts'}>
      {renderActionsRuleTabs(rule?.id, intl)}
      <TableToolbarView
        ouiaId={'actions-rule-hosts-table'}
        rows={rows}
        setLimit={setLimit}
        setOffset={setOffset}
        columns={columns(intl)}
        fetchData={updateHosts}
        pagination={defaultSettings}
        plural={intl.formatMessage(sharedMessages.hosts)}
        singular={intl.formatMessage(sharedMessages.host)}
        isLoading={isFetching || isFiltering}
        onFilterChange={handleFilterChange}
        renderEmptyState={() => (
          <TableEmptyState
            title={intl.formatMessage(sharedMessages.noactionsrulehosts)}
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
                ? intl.formatMessage(sharedMessages.noactionsrulehosts)
                : intl.formatMessage(sharedMessages.clearAllFiltersDescription)
            }
          />
        )}
      />
    </PageSection>
  );
};

export { ActionsRuleHosts };
