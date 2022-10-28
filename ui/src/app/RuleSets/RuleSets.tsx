import { PageSection, Title } from '@patternfly/react-core';
import { Route, useHistory } from 'react-router-dom';
import React, { useState, useEffect, useReducer, Fragment } from 'react';
import { Button } from '@patternfly/react-core';
import { TopToolbar } from '../shared/top-toolbar';
import { PlusCircleIcon } from '@patternfly/react-icons';
import sharedMessages from '../messages/shared.messages';
import { cellWidth } from '@patternfly/react-table';
import { TableToolbarView } from '@app/shared/table-toolbar-view';
import TableEmptyState from '@app/shared/table-empty-state';
import { useIntl } from 'react-intl';
import { defaultSettings } from '@app/shared/pagination';
import { NewRuleSet } from '@app/NewRuleSet/NewRuleSet';
import { createRows } from '@app/RuleSets/rule-sets-table-helpers';
import { AnyObject } from '@app/shared/types/common-types';
import { listRulesets } from '@app/API/Ruleset';

export interface SourceType {
  id: string;
  name?: string;
}

export interface InventoryType {
  id: string;
  name?: string;
  inventory?: string;
}
export interface PlaybookType {
  id: string;
  name?: string;
  playbook?: string;
}

export interface RuleType {
  id: string;
  name?: string;
  action?: AnyObject;
  description?: string;
  ruleset?: RuleSetType;
  type?: string;
  project_id?: string;
  project_name?: string;
  fired_count?: string;
  created_at?: string;
  modified_at?: string;
  last_fired_date?: string;
  extra_var_id?: string;
}

export interface RuleSetType {
  id: string;
  name?: string;
  sources?: SourceType[];
  rules?: RuleType[];
  rulesets: string;
}

const columns = (intl) => [
  {
    title: intl.formatMessage(sharedMessages.name),
    transforms: [cellWidth(50)],
  },
  {
    title: intl.formatMessage(sharedMessages.number_of_rules),
  },
];

const prepareChips = (filterValue, intl) =>
  filterValue
    ? [
        {
          category: intl.formatMessage(sharedMessages.name),
          key: 'url',
          chips: [{ name: filterValue, value: filterValue }],
        },
      ]
    : [];

const initialState = (filterValue = '') => ({
  filterValue,
  isFetching: true,
  isFiltering: false,
  selectedRuleSets: [],
  selectedAll: false,
  rows: [],
});

const areSelectedAll = (rows: RuleSetType[] = [], selected) => rows.every((row) => selected.includes(row.id));

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const RuleSetsListState = (state, action) => {
  switch (action.type) {
    case 'setRows':
      return {
        ...state,
        rows: action.payload,
        selectedAll: areSelectedAll(action.payload, state.selectedRuleSets),
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

const RuleSets: React.FunctionComponent = () => {
  const intl = useIntl();
  const history = useHistory();
  const [ruleSets, setRuleSets] = useState<RuleSetType[]>([]);
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);

  const meta = { count: ruleSets?.length || 0, limit, offset };
  const [{ filterValue, isFetching, isFiltering, selectedRuleSets, selectedAll, rows }, stateDispatch] = useReducer(
    RuleSetsListState,
    initialState()
  );

  const setSelectedRuleSets = (id) => stateDispatch({ type: 'select', payload: id });

  const updateRuleSets = (pagination) => {
    stateDispatch({ type: 'setFetching', payload: true });
    return listRulesets(pagination)
      .then(() => stateDispatch({ type: 'setFetching', payload: false }))
      .catch(() => stateDispatch({ type: 'setFetching', payload: false }));
  };

  useEffect(() => {
    listRulesets().then((data) => {
      setRuleSets(data.data);
      stateDispatch({ type: 'setRows', payload: createRows(ruleSets) });
    });
  }, []);

  useEffect(() => {
    updateRuleSets(defaultSettings);
  }, []);

  useEffect(() => {
    stateDispatch({ type: 'setRows', payload: createRows(ruleSets) });
  }, [ruleSets]);

  const clearFilters = () => {
    stateDispatch({ type: 'clearFilters' });
    return updateRuleSets(meta);
  };

  const handleFilterChange = (value) => {
    !value || value === '' ? clearFilters() : stateDispatch({ type: 'setFilterValue', payload: value });
  };

  const routes = () => (
    <Fragment>
      <Route exact path={'/new-rule-set'}>
        <NewRuleSet />
      </Route>
    </Fragment>
  );

  const actionResolver = () => [
    {
      title: intl.formatMessage(sharedMessages.disable),
      component: 'button',
      onClick: (_event, _rowId, ruleset) =>
        history.push({
          pathname: `/rulesets/${ruleset?.id}/disable`,
        }),
    },
  ];

  const anyRuleSetsSelected = selectedRuleSets.length > 0;

  const toolbarButtons = () => null;

  return (
    <Fragment>
      <TopToolbar>
        <Title headingLevel={'h2'}>Rule Sets</Title>
      </TopToolbar>
      <PageSection page-type={'ruleset-list'} id={'ruleset_list'}>
        <TableToolbarView
          ouiaId={'RuleSets-table'}
          rows={rows}
          columns={columns(intl)}
          fetchData={updateRuleSets}
          routes={routes}
          setLimit={setLimit}
          setOffset={setOffset}
          actionResolver={actionResolver}
          plural={intl.formatMessage(sharedMessages.rulesets)}
          singular={intl.formatMessage(sharedMessages.ruleset)}
          isLoading={isFetching || isFiltering}
          onFilterChange={handleFilterChange}
          renderEmptyState={() => (
            <TableEmptyState
              title={intl.formatMessage(sharedMessages.norulesets)}
              Icon={PlusCircleIcon}
              PrimaryAction={() =>
                filterValue !== '' ? (
                  <Button onClick={() => clearFilters()} variant="link">
                    {intl.formatMessage(sharedMessages.clearAllFilters)}
                  </Button>
                ) : null
              }
              description={
                filterValue === ''
                  ? intl.formatMessage(sharedMessages.norulesets)
                  : intl.formatMessage(sharedMessages.clearAllFiltersDescription)
              }
            />
          )}
        />
      </PageSection>
    </Fragment>
  );
};
export { RuleSets };
