import {Button, PageSection, SimpleListItem} from '@patternfly/react-core';
import {useHistory, useParams} from 'react-router-dom';
import React, {useEffect, useReducer, useState} from 'react';
import {TableToolbarView} from "@app/shared/table-toolbar-view";
import sharedMessages from "../messages/shared.messages";
import {cellWidth} from "@patternfly/react-table";
import TableEmptyState from "@app/shared/table-empty-state";
import {useIntl} from "react-intl";
import {defaultSettings} from "@app/shared/pagination";
import {createRows} from "./rulesets-table-helpers";
import {CubesIcon} from "@patternfly/react-icons";
import {renderRuleBookTabs, RuleBookType, RuleSetType} from "@app/RuleBook/rulebook";
import {getServer} from "@app/utils/utils";

const columns = (intl) => [
  {
    title: (intl.formatMessage(sharedMessages.name)),
    transforms: [cellWidth(40)]
  },
  {
    title: (intl.formatMessage(sharedMessages.number_of_rules))
  },
  {
    title: (intl.formatMessage(sharedMessages.fire_count))
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
  isFetching: false,
  isFiltering: false,
  rows: []
});

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const rulesetsListState = (state, action) => {
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
const endpoint_rulesets = 'http://' + getServer() + '/api/rulebook_json/';
const fetchRulebookRuleSets = (id, pagination=defaultSettings) =>
{
  return fetch(`${endpoint_rulesets}${id}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then(response => response.json()).then(data => ( data ? data.rulesets : []))
}

const RulebookRulesets: React.FunctionComponent<{rulebook: RuleBookType}> = ({rulebook}) => {
  const history = useHistory();
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);
  const [rulesets, setRuleSets] = useState<RuleSetType[]>([]);

  const rulebookId = rulebook?.id;
  const {id} = useParams<{id: string}>();

  const meta = {count: rulesets?.length || 0, limit, offset};
  const [
    {
      filterValue,
      isFetching,
      isFiltering,
      rows
    },
    stateDispatch
  ] = useReducer(rulesetsListState, initialState());

  const intl = useIntl();
  const updateRuleSets = (pagination) => {
    stateDispatch({type: 'setFetching', payload: true});
    return fetchRulebookRuleSets(id, pagination)
      .then(data => { setRuleSets(data); console.log( 'Debug - rulesets data: ', data);
        stateDispatch({type: 'setRows', payload: createRows(data)});})
      .then(() => stateDispatch({type: 'setFetching', payload: false}))
      .catch(() => stateDispatch({type: 'setFetching', payload: false}));
  };

  useEffect(() => {
    updateRuleSets(defaultSettings);
  }, []);

  const clearFilters = () => {
    stateDispatch({type: 'clearFilters'});
    return updateRuleSets(meta);
  };

  const handleFilterChange = (value) => {
    !value || value === ''
      ? clearFilters()
      : stateDispatch({type: 'setFilterValue', payload: value});
  };
  return (
    <PageSection page-type={'rulebook-rulesets'} id={'rulebook-rulesets'}>
      { renderRuleBookTabs(id, intl) }
      <TableToolbarView
        ouiaId={'rulebook-rulesets-table'}
        rows={rows}
        columns={columns(intl)}
        fetchData={updateRuleSets}
        setLimit={setLimit}
        setOffset={setOffset}
        plural={intl.formatMessage(sharedMessages.rulesets)}
        singular={intl.formatMessage(sharedMessages.ruleset)}
        isLoading={isFetching || isFiltering}
        onFilterChange={handleFilterChange}
        renderEmptyState={() => (
          <TableEmptyState
            title={intl.formatMessage(sharedMessages.norulebookrulesets)}
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
                ? intl.formatMessage(sharedMessages.norulebookrulesets)
                : intl.formatMessage(
                  sharedMessages.clearAllFiltersDescription
                )
            }
          />
        )}
      />
    </PageSection>
  );
}

export { RulebookRulesets };
