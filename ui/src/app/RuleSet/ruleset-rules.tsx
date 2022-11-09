import { Button, PageSection } from '@patternfly/react-core';
import { useParams } from 'react-router-dom';
import React, { useEffect, useReducer, useState } from 'react';
import { TableToolbarView } from '@app/shared/table-toolbar-view';
import sharedMessages from '../messages/shared.messages';
import { cellWidth } from '@patternfly/react-table';
import TableEmptyState from '@app/shared/table-empty-state';
import { useIntl } from 'react-intl';
import { defaultSettings } from '@app/shared/pagination';
import { createRows } from './rules-table-helpers';
import { CubesIcon } from '@patternfly/react-icons';
import { renderRuleSetFileTabs, RuleSetType, RuleType } from '@app/RuleSet/ruleset';
import { fetchRulesetRules } from '@app/API/Ruleset';

const columns = (intl) => [
  {
    title: intl.formatMessage(sharedMessages.name),
  },
  {
    title: intl.formatMessage(sharedMessages.condition),
    transforms: [cellWidth(40)],
  },
  {
    title: intl.formatMessage(sharedMessages.action),
  },
  {
    title: intl.formatMessage(sharedMessages.fire_count),
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
export const rulesListState = (state, action) => {
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

const RulesetRules: React.FunctionComponent<{ ruleset: RuleSetType }> = ({ ruleset }) => {
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);
  const [rules, setRules] = useState<RuleType[]>([]);

  const { id } = useParams<{ id: string }>();

  const meta = { count: rules?.length || 0, limit, offset };
  const [{ filterValue, isFetching, isFiltering, rows }, stateDispatch] = useReducer(rulesListState, initialState());

  const intl = useIntl();
  const updateRules = (pagination) => {
    stateDispatch({ type: 'setFetching', payload: true });
    return fetchRulesetRules(id, pagination)
      .then((data) => setRules(data?.data))
      .then(() => stateDispatch({ type: 'setFetching', payload: false }))
      .catch(() => stateDispatch({ type: 'setFetching', payload: false }));
  };

  useEffect(() => {
    fetchRulesetRules(id).then((data) => {
      stateDispatch({ type: 'setRows', payload: createRows(data) });
    });
  }, []);

  useEffect(() => {
    updateRules(defaultSettings);
  }, []);

  const clearFilters = () => {
    stateDispatch({ type: 'clearFilters' });
    return updateRules(meta);
  };

  const handleFilterChange = (value) => {
    !value || value === '' ? clearFilters() : stateDispatch({ type: 'setFilterValue', payload: value });
  };
  return (
    <PageSection page-type={'ruleset-rules'} id={'ruleset-rules'}>
      {renderRuleSetFileTabs(id, intl)}
      <TableToolbarView
        ouiaId={'ruleset-rules-table'}
        rows={rows}
        setLimit={setLimit}
        setOffset={setOffset}
        columns={columns(intl)}
        fetchData={updateRules}
        pagination={defaultSettings}
        plural={intl.formatMessage(sharedMessages.rules)}
        singular={intl.formatMessage(sharedMessages.rules)}
        isLoading={isFetching || isFiltering}
        onFilterChange={handleFilterChange}
        renderEmptyState={() => (
          <TableEmptyState
            title={intl.formatMessage(sharedMessages.norulesetrules)}
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
                ? intl.formatMessage(sharedMessages.norulesetrules)
                : intl.formatMessage(sharedMessages.clearAllFiltersDescription)
            }
          />
        )}
      />
    </PageSection>
  );
};

export { RulesetRules };
