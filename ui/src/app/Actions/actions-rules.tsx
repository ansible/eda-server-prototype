import { Button, PageSection } from '@patternfly/react-core';
import React, { useEffect, useReducer, useState } from 'react';
import { TableToolbarView } from '@app/shared/table-toolbar-view';
import sharedMessages from '../messages/shared.messages';
import TableEmptyState from '@app/shared/table-empty-state';
import { useIntl } from 'react-intl';
import { defaultSettings } from '@app/shared/pagination';
import { createRows } from './actions-rules-table-helpers';
import { CubesIcon } from '@patternfly/react-icons';
import { renderActionsTabs } from '@app/Actions/Actions';
import { ActionsRuleType } from '@app/Actions/Actions';
import { listActionsRules } from '@app/API/Actions';

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

const initialState = (filterValue = '') => ({
  filterValue,
  isFetching: false,
  isFiltering: false,
  rows: [],
});

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const actionsRulesListState = (state, action) => {
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

const ActionsRules: React.FunctionComponent = () => {
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);
  const [actionsRules, setActionsRules] = useState<ActionsRuleType[]>([]);

  const meta = { count: actionsRules?.length || 0, limit, offset };

  const [{ filterValue, isFetching, isFiltering, rows }, stateDispatch] = useReducer(
    actionsRulesListState,
    initialState()
  );

  const intl = useIntl();
  const updateActionsRules = (pagination) => {
    stateDispatch({ type: 'setFetching', payload: true });
    return listActionsRules(pagination)
      .then((data) => {
        setActionsRules(data?.data);
        return stateDispatch({ type: 'setFetching', payload: false });
      })
      .catch(() => stateDispatch({ type: 'setFetching', payload: false }));
  };

  useEffect(() => {
    updateActionsRules(defaultSettings);
  }, []);

  useEffect(() => {
    stateDispatch({ type: 'setRows', payload: createRows(actionsRules, intl) });
  }, [actionsRules]);

  const clearFilters = () => {
    stateDispatch({ type: 'clearFilters' });
    return updateActionsRules(meta);
  };

  const handleFilterChange = (value) => {
    !value || value === '' ? clearFilters() : stateDispatch({ type: 'setFilterValue', payload: value });
  };

  return (
    <PageSection page-type={'activation-details'} id={'activation-details'}>
      {renderActionsTabs(intl)}
      <TableToolbarView
        ouiaId={'actions-rules-table'}
        rows={rows}
        setLimit={setLimit}
        setOffset={setOffset}
        columns={columns(intl)}
        fetchData={updateActionsRules}
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

export { ActionsRules };
