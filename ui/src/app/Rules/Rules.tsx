import {Checkbox, PageSection, Title, ToolbarGroup, ToolbarItem} from '@patternfly/react-core';
import {Link, Route, useHistory} from 'react-router-dom';
import React, {useState, useEffect, useReducer, Fragment} from 'react';
import { Button } from '@patternfly/react-core';
import {getServer} from '@app/utils/utils';
import {TopToolbar} from '../shared/top-toolbar';
import { PlusCircleIcon } from '@patternfly/react-icons';
import sharedMessages from '../messages/shared.messages';
import {TableToolbarView} from "@app/shared/table-toolbar-view";
import TableEmptyState from "@app/shared/table-empty-state";
import {useIntl} from "react-intl";
import {defaultSettings} from "@app/shared/pagination";
import {createRows} from "@app/Rules/rules-table-helpers";

export interface RuleType {
  id: string;
  name: string;
  description: string,
  extra_var_id?: string,
  execution_environment?: string,
  playbook?: string,
  restarted_count?: string,
  restart_policy?: string,
  last_restarted?: string,
  status?: string,
  ruleset_id?: string,
  ruleset_name?: string,
  inventory_id?: string,
  inventory_name?: string,
  created_at?: string,
  updated_at?: string
}

const endpoint = 'http://' + getServer() + '/api/rules/';

const columns = (intl) => [
  {
  title: (intl.formatMessage(sharedMessages.name))
  },
  {
    title: (intl.formatMessage(sharedMessages.ruleset))
  },
  {
    title: (intl.formatMessage(sharedMessages.action))
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
  isFetching: true,
  isFiltering: false,
  rows: []
});

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const rulesListState = (state, action) => {
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

const fetchRules = (pagination = defaultSettings) => fetch(endpoint, {
  headers: {
    'Content-Type': 'application/json',
  },
});

const Rules: React.FunctionComponent = () => {
  const intl = useIntl();
  const history = useHistory();
  const [rules, setRules] = useState<RuleType[]>([]);
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);

  const data = rules;
  const meta = {count: rules?.length || 0, limit, offset};
  const [
    {
      filterValue,
      isFetching,
      isFiltering,
      rows
    },
    stateDispatch
  ] = useReducer(rulesListState, initialState());

  const setSelectedRules = (id) =>
    stateDispatch({type: 'select', payload: id});

  const updateRules = (pagination) => {
    stateDispatch({type: 'setFetching', payload: true});
    return fetchRules(pagination)
      .then(() => stateDispatch({type: 'setFetching', payload: false}))
      .catch(() => stateDispatch({type: 'setFetching', payload: false}));
  };

  useEffect(() => {
    fetchRules().then(response => response.json())
      .then(data => { setRules(data); stateDispatch({type: 'setRows', payload: createRows(rules)});});
  }, []);

  useEffect(() => {
    updateRules(defaultSettings);
  }, []);

  useEffect(() => {
    stateDispatch({type: 'setRows', payload: createRows(rules)});
  }, [rules]);

  const clearFilters = () => {
    stateDispatch({type: 'clearFilters'});
    return updateRules(meta);
  };

  const handleFilterChange = (value) => {
    !value || value === ''
      ? clearFilters()
      : stateDispatch({type: 'setFilterValue', payload: value});
  };

  return (
    <Fragment>
      <TopToolbar>
        <Title headingLevel={"h2"}>{intl.formatMessage(sharedMessages.rules)}</Title>
      </TopToolbar>
      <PageSection page-type={'rules-list'} id={'rules_list'}>
        <TableToolbarView
          ouiaId={'rules-table'}
          rows={rows}
          columns={columns(intl)}
          fetchData={updateRules}
          plural={intl.formatMessage(sharedMessages.rules)}
          singular={intl.formatMessage(sharedMessages.rule)}
          isLoading={isFetching || isFiltering}
          onFilterChange={handleFilterChange}
          renderEmptyState={() => (
            <TableEmptyState
              title={intl.formatMessage(sharedMessages.noprojects)}
              Icon={PlusCircleIcon}
              PrimaryAction={() =>
                filterValue !== '' ? (
                  <Button onClick={() => clearFilters()} variant="link">
                    {intl.formatMessage(sharedMessages.clearAllFilters)}
                  </Button>
                ) : (
                  <Link
                    id="create-project-link"
                    to={{pathname: '/new-project'}}
                  >
                    <Button
                      ouiaId={'create-project-link'}
                      variant="primary"
                      aria-label={intl.formatMessage(
                        sharedMessages.add_new_project
                      )}
                    >
                      {intl.formatMessage(sharedMessages.add_new_project)}
                    </Button>
                  </Link>
                )
              }
              description={
                filterValue === ''
                  ? intl.formatMessage(sharedMessages.noprojects)
                  : intl.formatMessage(
                  sharedMessages.clearAllFiltersDescription
                  )
              }
            />
          )}
        />
      </PageSection>
    </Fragment>
  );
}
export { Rules };
