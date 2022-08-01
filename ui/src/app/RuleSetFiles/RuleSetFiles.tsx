import {PageSection, Title} from '@patternfly/react-core';
import {Route, useHistory} from 'react-router-dom';
import React, {useState, useEffect, useReducer, Fragment} from 'react';
import { Button } from '@patternfly/react-core';
import {getServer} from '@app/utils/utils';
import {TopToolbar} from '../shared/top-toolbar';
import { PlusCircleIcon } from '@patternfly/react-icons';
import sharedMessages from '../messages/shared.messages';
import {cellWidth} from "@patternfly/react-table";
import {TableToolbarView} from "@app/shared/table-toolbar-view";
import TableEmptyState from "@app/shared/table-empty-state";
import isEmpty from 'lodash/isEmpty';
import {useIntl} from "react-intl";
import {defaultSettings} from "@app/shared/pagination";
import {NewRuleSet} from "@app/NewRuleSet/NewRuleSet";
import {createRows} from "@app/RuleSetFiles/rule-sets-table-helpers";

interface RuleSetType {
  id: string;
  git_hash?: string;
  url: string;
}

const endpoint = 'http://' + getServer() + '/api/rule_set_files/';

const columns = (intl) => [
  {
    title: intl.formatMessage(sharedMessages.name),
    transforms: [cellWidth(50)]
  },
  {
    title: intl.formatMessage(sharedMessages.number_of_rules)
  },
  {
    title: intl.formatMessage(sharedMessages.fire_count)
  }
];

const prepareChips = (filterValue, intl) =>
  filterValue
    ? [
      {
        category: intl.formatMessage(sharedMessages.name),
        key: 'url',
        chips: [{ name: filterValue, value: filterValue }]
      }
    ]
    : [];

const initialState = (filterValue = '') => ({
  filterValue,
  isFetching: true,
  isFiltering: false,
  selectedRuleSets: [],
  selectedAll: false,
  rows: []
});

const areSelectedAll = (rows = [], selected) =>
  rows.every((row) => selected.includes(row.id));

const unique = (value, index, self) => self.indexOf(value) === index;

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const RuleSetsListState = (state, action) => {
  switch (action.type) {
    case 'setRows':
      return {
        ...state,
        rows: action.payload,
        selectedAll: areSelectedAll(action.payload, state.selectedRuleSets)
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

const fetchRuleSets = (pagination = defaultSettings) => fetch(endpoint, {
  headers: {
    'Content-Type': 'application/json',
  },
});

const RuleSets: React.FunctionComponent = () => {
  const intl = useIntl();
  const history = useHistory();
  const [RuleSets, setRuleSets] = useState<RuleSetType[]>([]);
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);

  const data = RuleSets;
  const meta = {count: RuleSets?.length || 0, limit, offset};
  const [
    {
      filterValue,
      isFetching,
      isFiltering,
      selectedRuleSets,
      selectedAll,
      rows
    },
    stateDispatch
  ] = useReducer(RuleSetsListState, initialState());

  const setSelectedRuleSets = (id) =>
    stateDispatch({type: 'select', payload: id});

  const updateRuleSets = (pagination) => {
    stateDispatch({type: 'setFetching', payload: true});
    return fetchRuleSets(pagination)
      .then(() => stateDispatch({type: 'setFetching', payload: false}))
      .catch(() => stateDispatch({type: 'setFetching', payload: false}));
  };

  useEffect(() => {
    fetchRuleSets().then(response => response.json())
      .then(data => { setRuleSets(data); stateDispatch({type: 'setRows', payload: createRows(RuleSets)});});
  }, []);

  useEffect(() => {
    updateRuleSets(defaultSettings);
  }, []);

  useEffect(() => {
    stateDispatch({type: 'setRows', payload: createRows(RuleSets)});
  }, [RuleSets]);

  const clearFilters = () => {
    stateDispatch({type: 'clearFilters'});
    return updateRuleSets(meta);
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
        path={'/new-rule-set'}
        render={(props) => (
          <NewRuleSet {...props} />
        )}
      />
    </Fragment>
  );

  const actionResolver = () => [
    {
      title: intl.formatMessage(sharedMessages.disable),
      component: 'button',
      onClick: (_event, _rowId, ruleset) =>
        history.push({
          pathname: '/disable-rule-set',
          search: `?rule-set=${ruleset.id}`
        })
    }
  ];

  const anyRuleSetsSelected = selectedRuleSets.length > 0;

  const toolbarButtons = () => null;

  return (
    <Fragment>
      <TopToolbar>
        <Title headingLevel={"h2"}>Rule Sets</Title>
      </TopToolbar>
      <PageSection>
        <TableToolbarView
          ouiaId={'RuleSets-table'}
          rows={rows}
          columns={columns(intl)}
          fetchData={updateRuleSets}
          routes={routes}
          actionResolver={actionResolver}
          titlePlural={intl.formatMessage(sharedMessages.rulesets)}
          titleSingular={intl.formatMessage(sharedMessages.ruleset)}
          isLoading={isFetching || isFiltering}
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
    </Fragment>
  );
}
export { RuleSets };
