import {Checkbox, PageSection, Title, ToolbarGroup, ToolbarItem} from '@patternfly/react-core';
import {Link, Route, useHistory} from 'react-router-dom';
import React, {useState, useEffect, useReducer, Fragment} from 'react';
import { Button } from '@patternfly/react-core';
import {getServer} from '@app/utils/utils';
import {TopToolbar} from '../shared/top-toolbar';
import { PlusCircleIcon } from '@patternfly/react-icons';
import sharedMessages from '../messages/shared.messages';
import {cellWidth} from "@patternfly/react-table";
import InventoriesTableContext from './inventories-table-context';
import {TableToolbarView} from "@app/shared/table-toolbar-view";
import TableEmptyState from "@app/shared/table-empty-state";
import {useIntl} from "react-intl";
import {defaultSettings} from "@app/shared/pagination";
import {NewInventory} from "@app/NewInventory/NewInventory";
import {createRows} from "@app/Inventories/inventories-table-helpers";
import {AnyObject} from "@app/shared/types/common-types";
import {RemoveInventory} from "@app/RemoveInventory/RemoveInventory";
import {listInventories} from "@app/API/Inventory";

export interface InventoryType {
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

const columns = (intl) => [
  {
    title: (''),
    transforms: [cellWidth(10 )]
  },
  {
    title: (intl.formatMessage(sharedMessages.name))
  },
  {
    title: (intl.formatMessage(sharedMessages.source_of_inventory))
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
  selectedInventories: [],
  selectedAll: false,
  rows: []
});

const areSelectedAll = (rows:InventoryType[] = [], selected) =>
  rows.every((row) => selected.includes(row.id));

const unique = (value, index, self) => self.indexOf(value) === index;

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const inventoriesListState = (state, action) => {
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
    case 'select':
      return {
        ...state,
        selectedAll: false,
        selectedInventories: state.selectedInventories.includes(action.payload)
          ? state.selectedInventories.filter((id) => id !== action.payload)
          : [...state.selectedInventories, action.payload]
      };
    case 'selectAll':
      return {
        ...state,
        selectedInventories: [
          ...state.selectedInventories,
          ...action.payload
        ].filter(unique),
        selectedAll: true
      };
    case 'unselectAll':
      return {
        ...state,
        selectedInventories: state.selectedInventories.filter(
          (selected) => !action.payload.includes(selected)
        ),
        selectedAll: false
      };
    case 'resetSelected':
      return {
        ...state,
        selectedInventories: [],
        selectedAll: false
      };
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
  ] = useReducer(inventoriesListState, initialState());

  const setSelectedInventories = (ids: string[]) =>
    stateDispatch({type: 'select', payload: ids});

  const handlePagination = (pagination) => {
    stateDispatch({type: 'setFetching', payload: true});
    return listInventories(pagination).then(data => { setInventories(data); stateDispatch({type: 'setRows', payload: createRows(inventories)});})
      .then(() => {stateDispatch({type: 'setFetching', payload: false});})
      .catch(() => stateDispatch({type: 'setFetching', payload: false}));
  };

  useEffect(() => {
    handlePagination(defaultSettings);
  }, []);

  useEffect(() => {
    stateDispatch({type: 'setRows', payload: createRows(inventories)});
  }, [inventories]);

  const clearFilters = () => {
    stateDispatch({type: 'clearFilters'});
    return handlePagination(meta);
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
        path={'/new-inventory'}>
        <NewInventory/>
      </Route>
      <Route exact path="/inventories/remove"
             render={ props => <RemoveInventory { ...props }
                                              ids={ selectedInventories }
                                              fetchData={ handlePagination }
                                              resetSelectedInventories={() =>
                                                stateDispatch({ type: 'resetSelected' })
                                              }/>}/>
      <Route exact path="/inventories/remove/:id"
             render={ props => <RemoveInventory { ...props }
                                              fetchData={ handlePagination }
             /> }/>
    </Fragment>
  );

  const actionResolver = () => [
    {
      title: intl.formatMessage(sharedMessages.edit),
      component: 'button',
      onClick: (_event, _rowId, inventory) =>
        history.push({
          pathname: `/inventories/edit-inventory/${inventory.id}`
        })
    },
    {
      title: intl.formatMessage(sharedMessages.delete),
      component: 'button',
      onClick: (_event, _rowId, inventory) =>
        history.push({
          pathname: `/inventories/remove/${inventory.id}`
        })
    }
  ];

  const selectAllFunction = () =>
      stateDispatch({type: 'selectAll', payload: data.map(( item) =>  item.id)});
  const unselectAllFunction = () =>
    stateDispatch({type: 'unselectAll', payload: data.map(( item) =>  item.id)});

  const anyInventoriesSelected = selectedInventories.length > 0;

  const bulkSelectProps = React.useMemo(() => {
    return {
      count: selectedInventories.length || 0,
      items: [
        {
          title: 'Select none (0)',
          onClick: unselectAllFunction
        },
        {
          title: `Select all (${inventories.length || 0})`,
          onClick: selectAllFunction
        }
      ],
      checked: selectedInventories.length === inventories.length,
      onSelect: (isChecked: boolean) => isChecked ? selectAllFunction() : unselectAllFunction()
    };
  }, [ selectedInventories.length, inventories.length ]);

  const toolbarButtons = () => (
    <ToolbarGroup className={`pf-u-pl-lg top-toolbar`}>
      <ToolbarItem>
        <Link
          id="add-inventory-link"
          to={{pathname: '/new-inventory'}}
        >
          <Button
            ouiaId={'add-inventory-link'}
            variant="primary"
            aria-label={intl.formatMessage(sharedMessages.addInventory)}
          >
            {intl.formatMessage(sharedMessages.addInventory)}
          </Button>
        </Link>
      </ToolbarItem>
      <ToolbarItem>
        <Link
          id="remove-multiple-inventories"
          className={anyInventoriesSelected ? '' : 'disabled-link'}
          to={{pathname: '/inventories/remove'}}
        >
          <Button
            variant="secondary"
            isDisabled={!anyInventoriesSelected}
            aria-label={intl.formatMessage(
              sharedMessages.deleteInventoryTitle
            )}
          >
            {intl.formatMessage(sharedMessages.delete)}
          </Button>
        </Link>
      </ToolbarItem>
    </ToolbarGroup>
  );

  return (
    <Fragment>
      <TopToolbar>
        <Title headingLevel={"h2"}>{intl.formatMessage(sharedMessages.inventories)}</Title>
      </TopToolbar>
      <InventoriesTableContext.Provider
        value={{
          selectedInventories,
          setSelectedInventories
        }}
      >
        <PageSection page-type={'inventories-list'} id={'inventories_list'}>
          <TableToolbarView
            ouiaId={'inventories-table'}
            rows={rows}
            setLimit={setLimit}
            setOffset={setOffset}
            columns={columns(intl)}
            bulkSelect={bulkSelectProps}
            fetchData={handlePagination}
            routes={routes}
            actionResolver={actionResolver}
            plural={intl.formatMessage(sharedMessages.inventories)}
            singular={intl.formatMessage(sharedMessages.inventory)}
            toolbarButtons={toolbarButtons}
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
                  ) : (
                    <Link
                      id="create-inventory-link"
                      to={{pathname: '/new-inventory'}}
                    >
                      <Button
                        ouiaId={'create-inventory-link'}
                        variant="primary"
                        aria-label={intl.formatMessage(
                          sharedMessages.addInventory
                        )}
                      >
                        {intl.formatMessage(sharedMessages.addInventory)}
                      </Button>
                    </Link>
                  )
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
      </InventoriesTableContext.Provider>
    </Fragment>
  );
}
export { Inventories };
