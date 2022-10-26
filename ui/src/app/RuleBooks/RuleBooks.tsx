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
import {useIntl} from "react-intl";
import {defaultSettings} from "@app/shared/pagination";
import {createRows} from "@app/RuleBooks/rulebooks-table-helpers";
import {RuleSetType} from "@app/RuleSet/ruleset";
import {RuleBookType} from "@app/RuleBook/rulebook";

const endpoint = 'http://' + getServer() + '/api/rulebooks';

const columns = (intl) => [
  {
    title: intl.formatMessage(sharedMessages.name),
    transforms: [cellWidth(50)]
  },
  {
    title: intl.formatMessage(sharedMessages.number_of_rulesets)
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
  selectedRuleBooks: [],
  selectedAll: false,
  rows: []
});

const areSelectedAll = (rows:RuleSetType[] = [], selected) =>
  rows.every((row) => selected.includes(row.id));

const unique = (value, index, self) => self.indexOf(value) === index;

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const RuleSetsListState = (state, action) => {
  switch (action.type) {
    case 'setRows':
      return {
        ...state,
        rows: action.payload,
        selectedAll: areSelectedAll(action.payload, state.selectedRuleBooks)
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

const fetchRuleBooks = (pagination = defaultSettings) => fetch(endpoint, {
  headers: {
    'Content-Type': 'application/json',
  },
});

const RuleBooks: React.FunctionComponent = () => {
  const intl = useIntl();
  const history = useHistory();
  const [ruleBooks, setRuleBooks] = useState<RuleBookType[]>([]);
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);

  const data = ruleBooks;
  const meta = {count: ruleBooks?.length || 0, limit, offset};
  const [
    {
      filterValue,
      isFetching,
      isFiltering,
      selectedRuleBooks,
      selectedAll,
      rows
    },
    stateDispatch
  ] = useReducer(RuleSetsListState, initialState());

  const setSelectedRuleBooks = (id) =>
    stateDispatch({type: 'select', payload: id});

  const updateRuleBooks = (pagination) => {
    stateDispatch({type: 'setFetching', payload: true});
    return fetchRuleBooks(pagination)
      .then(() => stateDispatch({type: 'setFetching', payload: false}))
      .catch(() => stateDispatch({type: 'setFetching', payload: false}));
  };

  useEffect(() => {
    fetchRuleBooks().then(response => response.json())
      .then(data => { setRuleBooks(data);
        stateDispatch({type: 'setRows', payload: createRows(ruleBooks)});});
  }, []);
``
  useEffect(() => {
    updateRuleBooks(defaultSettings);
  }, []);

  useEffect(() => {
    stateDispatch({type: 'setRows', payload: createRows(ruleBooks)});
  }, [ruleBooks]);

  const clearFilters = () => {
    stateDispatch({type: 'clearFilters'});
    return updateRuleBooks(meta);
  };

  const handleFilterChange = (value) => {
    !value || value === ''
      ? clearFilters()
      : stateDispatch({type: 'setFilterValue', payload: value});
  };

  const actionResolver = () => [
    {
      title: intl.formatMessage(sharedMessages.disable),
      component: 'button',
      onClick: (_event, _rowId, rulebook) =>
        history.push({
          pathname: `/rulebooks/relaunch/${rulebook?.id}`,
        })
    }
  ];

  const anyRuleBooksSelected = selectedRuleBooks.length > 0;

  const toolbarButtons = () => null;

  return (
    <Fragment>
      <TopToolbar>
        <Title headingLevel={"h2"}>Rulebooks</Title>
      </TopToolbar>
      <PageSection page-type={'rulebooks-list'} id={'rulebooks_list'}>
        <TableToolbarView
          ouiaId={'RuleBooks-table'}
          rows={rows}
          columns={columns(intl)}
          fetchData={updateRuleBooks}
          setLimit={setLimit}
          setOffset={setOffset}
          actionResolver={actionResolver}
          plural={intl.formatMessage(sharedMessages.rulebooks)}
          singular={intl.formatMessage(sharedMessages.rulebook)}
          isLoading={isFetching || isFiltering}
          onFilterChange={handleFilterChange}
          renderEmptyState={() => (
            <TableEmptyState
              title={intl.formatMessage(sharedMessages.norulebooks)}
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
                  ? intl.formatMessage(sharedMessages.norulebooks)
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
export { RuleBooks };
