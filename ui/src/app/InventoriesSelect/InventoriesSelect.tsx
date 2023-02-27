import {
  Flex,
  FlexItem,
  Label,
  Level,
  LevelItem,
  Modal,
  ModalVariant,
  PageSection,
  Title,
} from '@patternfly/react-core';
import { Link } from 'react-router-dom';
import React, { useState, useEffect, useReducer, Fragment } from 'react';
import { Button } from '@patternfly/react-core';
import { TopToolbar } from '../shared/top-toolbar';
import { PlusCircleIcon } from '@patternfly/react-icons';
import sharedMessages from '../messages/shared.messages';
import { cellWidth } from '@patternfly/react-table';
import InventoriesSelectTableContext from './inventories-select-table-context';
import { TableToolbarView } from '@app/shared/table-toolbar-view';
import TableEmptyState from '@app/shared/table-empty-state';
import { useIntl } from 'react-intl';
import { defaultSettings } from '@app/shared/pagination';
import { createRows } from '@app/InventoriesSelect/inventories-select-table-helpers';
import { listInventories } from '@app/API/Inventory';

export interface InventorySelectType {
  id: string;
  name?: string;
  description?: string;
}

interface InventoriesSelectParam {
  isModalOpen: boolean;
  setIsModalOpen: any;
  inventory: InventorySelectType | undefined;
  setInventory: any;
}

const columns = (intl) => [
  {
    title: '',
    transforms: [cellWidth(10)],
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

const initialState = (filterValue = '', inventory = undefined) => ({
  filterValue,
  isFetching: true,
  isFiltering: false,
  selectedInventory: inventory,
  rows: [],
});

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const inventoriesSelectListState = (state, action) => {
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
    case 'select':
      return {
        ...state,
        selectedInventory: action.payload,
      };
    case 'resetSelected':
      return {
        ...state,
        selectedInventory: undefined,
      };
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

const InventoriesSelect: React.FunctionComponent<InventoriesSelectParam> = ({
  isModalOpen,
  setIsModalOpen,
  inventory,
  setInventory,
}) => {
  const intl = useIntl();
  const [inventories, setInventories] = useState<InventorySelectType[]>([]);
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);
  const meta = { count: inventories?.length || 0, limit, offset };
  const [{ filterValue, isFetching, isFiltering, selectedInventory, rows }, stateDispatch] = useReducer(
    inventoriesSelectListState,
    initialState()
  );
  const handleModalToggle = () => {
    setIsModalOpen(!isModalOpen);
  };
  const setSelectedInventory = (inventory: InventorySelectType | undefined) =>
    stateDispatch({ type: 'select', payload: inventory });

  const handlePagination = (pagination) => {
    stateDispatch({ type: 'setFetching', payload: true });
    return listInventories(pagination)
      .then((data) => {
        setInventories(data.data);
        stateDispatch({ type: 'setRows', payload: createRows(inventories) });
      })
      .then(() => {
        stateDispatch({ type: 'setFetching', payload: false });
      })
      .catch(() => stateDispatch({ type: 'setFetching', payload: false }));
  };

  useEffect(() => {
    handlePagination(defaultSettings);
  }, []);

  useEffect(() => {
    stateDispatch({ type: 'setRows', payload: createRows(inventories) });
  }, [inventories]);

  const clearFilters = () => {
    stateDispatch({ type: 'clearFilters' });
    return handlePagination(meta);
  };

  return (
    <Fragment>
      <Modal
        variant={ModalVariant.medium}
        title={intl.formatMessage(sharedMessages.selectInventory)}
        isOpen={isModalOpen}
        onClose={handleModalToggle}
        actions={[
          <Button
            key="confirm"
            variant="primary"
            onClick={() => {
              setInventory(selectedInventory);
              handleModalToggle();
            }}
          >
            Select
          </Button>,
          <Button key="cancel" variant="link" onClick={handleModalToggle}>
            Cancel
          </Button>,
        ]}
      >
        <InventoriesSelectTableContext.Provider
          value={{
            selectedInventory,
            setSelectedInventory,
          }}
        >
          {selectedInventory && (
            <TopToolbar>
              <Flex>
                <FlexItem>
                  <Title headingLevel={'h6'}>{intl.formatMessage(sharedMessages.selected)}</Title>
                </FlexItem>
                <FlexItem>
                  <Label color="blue" onClose={() => setSelectedInventory(undefined)}>
                    {`${selectedInventory.name}`}
                  </Label>
                </FlexItem>
              </Flex>
            </TopToolbar>
          )}

          <TableToolbarView
            ouiaId={'inventories-table'}
            rows={rows}
            columns={columns(intl)}
            fetchData={handlePagination}
            plural={intl.formatMessage(sharedMessages.inventories)}
            singular={intl.formatMessage(sharedMessages.inventory)}
            isLoading={isFetching || isFiltering}
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
                    <Link id="create-inventory-link" to={{ pathname: '/inventories/add' }}>
                      <Button
                        ouiaId={'create-inventory-link'}
                        variant="primary"
                        aria-label={intl.formatMessage(sharedMessages.addInventory)}
                      >
                        {intl.formatMessage(sharedMessages.addInventory)}
                      </Button>
                    </Link>
                  )
                }
                description={
                  filterValue === ''
                    ? intl.formatMessage(sharedMessages.noinventories_action)
                    : intl.formatMessage(sharedMessages.clearAllFiltersDescription)
                }
              />
            )}
          />
        </InventoriesSelectTableContext.Provider>
      </Modal>
    </Fragment>
  );
};
export { InventoriesSelect };
