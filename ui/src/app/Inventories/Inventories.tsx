import {PageSection, Title} from '@patternfly/react-core';
import {useHistory} from 'react-router-dom';
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
import {createRows} from "@app/Inventories/inventories-table-helpers";
import {InventoryType} from "@app/Inventory/inventory";

const endpoint = 'http://' + getServer() + '/api/inventories/';

const columns = (intl) => [
  {
    title: intl.formatMessage(sharedMessages.name)
  },
  {
    title: intl.formatMessage(sharedMessages.source_of_inventory)
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
  selectedinventories: [],
  selectedAll: false,
  rows: []
});

const areSelectedAll = (rows:InventoryType[] = [], selected) =>
  rows.every((row) => selected.includes(row.id));

const unique = (value, index, self) => self.indexOf(value) === index;

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const InventoriesListState = (state, action) => {
  switch (action.type) {
    case 'setRows':
      return {
        ...state,
        rows: action.payload,
        selectedAll: areSelectedAll(action.payload, state.selectedInventories)
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

const fetchInventories = (pagination = defaultSettings) => fetch(endpoint, {
  headers: {
    'Content-Type': 'application/json',
  },
});

const Inventories: React.FunctionComponent = () => {
  const intl = useIntl();
  const history = useHistory();
  const [inventories, setInventories] = useState<InventoryType[]>([]);
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);

  const data = inventories;
  const meta = {count: inventories?.length || 0, limit, offset};
  const [
    {
      filterValue,
      isFetching,
      isFiltering,
      selectedInventories,
      selectedAll,
      rows
    },
    stateDispatch
  ] = useReducer(InventoriesListState, initialState());

  const setSelectedInventories = (id) =>
    stateDispatch({type: 'select', payload: id});

  const updateInventories = (pagination) => {
    stateDispatch({type: 'setFetching', payload: true});
    return fetchInventories(pagination)
      .then(() => stateDispatch({type: 'setFetching', payload: false}))
      .catch(() => stateDispatch({type: 'setFetching', payload: false}));
  };

  useEffect(() => {
    fetchInventories().then(response => response.json())
      .then(data => { setInventories(data); console.log( 'Debug - inventories data: ', data);
        stateDispatch({type: 'setRows', payload: createRows(inventories)});});
  }, []);
``
  useEffect(() => {
    updateInventories(defaultSettings);
  }, []);

  useEffect(() => {
    stateDispatch({type: 'setRows', payload: createRows(inventories)});
  }, [inventories]);

  const clearFilters = () => {
    stateDispatch({type: 'clearFilters'});
    return updateInventories(meta);
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
      onClick: (_event, _rowId, inventory) =>
        history.push({
          pathname: `/inventories/remove/${inventory.id}`
        })
    }
  ];

  const anyInventoriesSelected = selectedInventories.length > 0;

  const toolbarButtons = () => null;

  return (
    <Fragment>
      <TopToolbar>
        <Title headingLevel={"h2"}>inventories</Title>
      </TopToolbar>
      <PageSection page-type={'inventories-list'} id={'inventories_list'}>
        <TableToolbarView
          ouiaId={'inventories-table'}
          rows={rows}
          columns={columns(intl)}
          fetchData={updateInventories}
          setLimit={setLimit}
          setOffset={setOffset}
          actionResolver={actionResolver}
          plural={intl.formatMessage(sharedMessages.inventories)}
          singular={intl.formatMessage(sharedMessages.inventory)}
          isLoading={isFetching || isFiltering}
          onFilterChange={handleFilterChange}
          renderEmptyState={() => (
            <TableEmptyState
              title={intl.formatMessage(sharedMessages.noinventories_description)}
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
                  ? intl.formatMessage(sharedMessages.noinventories_action)
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
export { Inventories };
