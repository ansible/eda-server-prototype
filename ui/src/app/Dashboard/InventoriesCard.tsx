import { Card, CardBody, CardFooter, CardTitle, Level, LevelItem, Title } from '@patternfly/react-core';
import { Link, useHistory } from 'react-router-dom';
import React, { useState, useEffect, useReducer, Fragment } from 'react';
import { Button } from '@patternfly/react-core';
import { PlusCircleIcon } from '@patternfly/react-icons';
import sharedMessages from '../messages/shared.messages';
import { TableToolbarView } from '@app/shared/table-toolbar-view';
import TableEmptyState from '@app/shared/table-empty-state';
import { useIntl } from 'react-intl';
import { defaultSettings } from '@app/shared/pagination';
import { listInventories } from '@app/API/Inventory';

interface InventoryCardType {
  id: string;
  name: string;
  status?: string;
}

const createRows = (data: InventoryCardType[]) =>
  data.slice(-4).map(({ id, name, status }) => ({
    id,
    cells: [
      <Fragment key={`[inventory-${id}`}>
        <Link
          to={{
            pathname: `/inventories/inventory/${id}`,
          }}
        >
          {name}
        </Link>
      </Fragment>,
      status,
    ],
  }));

const columns = (intl) => [
  {
    title: intl.formatMessage(sharedMessages.name),
  },
  {
    title: intl.formatMessage(sharedMessages.source_of_inventory),
  },
];

const initialState = () => ({
  isFetching: true,
  rows: [],
});

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const inventoriesListState = (state, action) => {
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
    default:
      return state;
  }
};

const InventoriesCard: React.FunctionComponent = () => {
  const intl = useIntl();
  const [inventories, setInventories] = useState<InventoryCardType[]>([]);
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);
  const [{ isFetching, rows }, stateDispatch] = useReducer(inventoriesListState, initialState());
  const history = useHistory();

  const updateRows = () => {
    stateDispatch({ type: 'setFetching', payload: true });
    return listInventories()
      .then((data) => {
        setInventories(data?.data);
        stateDispatch({ type: 'setRows', payload: createRows(inventories) });
      })
      .then(() => {
        stateDispatch({ type: 'setFetching', payload: false });
      })
      .catch(() => stateDispatch({ type: 'setFetching', payload: false }));
  };

  useEffect(() => {
    updateRows();
  }, []);

  useEffect(() => {
    stateDispatch({ type: 'setRows', payload: createRows(inventories) });
  }, [inventories]);

  return (
    <Fragment>
      <Card style={{ transition: 'box-shadow 0.25s', minHeight: 575 }}>
        <CardTitle>
          <Level>
            <LevelItem>
              <Title headingLevel={'h2'}>{intl.formatMessage(sharedMessages.inventories)}</Title>
            </LevelItem>
            <LevelItem>
              <Button variant="link" onClick={() => history.push('/inventories')}>
                {intl.formatMessage(sharedMessages.go_to_inventories)}
              </Button>
            </LevelItem>
          </Level>
        </CardTitle>
        <CardBody>
          <TableToolbarView
            ouiaId={'inventories-table'}
            rows={rows}
            setLimit={setLimit}
            setOffset={setOffset}
            columns={columns(intl)}
            fetchData={updateRows}
            plural={intl.formatMessage(sharedMessages.inventories)}
            singular={intl.formatMessage(sharedMessages.inventory)}
            isLoading={isFetching}
            renderEmptyState={() => (
              <TableEmptyState
                title={intl.formatMessage(sharedMessages.noinventories_description)}
                Icon={PlusCircleIcon}
                PrimaryAction={() => (
                  <Link id="create-inventory-link" to={{ pathname: '/new-inventory' }}>
                    <Button
                      ouiaId={'create-inventory-link'}
                      variant="primary"
                      aria-label={intl.formatMessage(sharedMessages.addInventory)}
                    >
                      {intl.formatMessage(sharedMessages.addInventory)}
                    </Button>
                  </Link>
                )}
                description={intl.formatMessage(sharedMessages.noinventories_action)}
              />
            )}
          />
        </CardBody>
        <CardFooter>
          <Button variant="link" icon={<PlusCircleIcon />} onClick={() => history.push('/new-inventory')}>
            {intl.formatMessage(sharedMessages.create_inventory)}
          </Button>
        </CardFooter>
      </Card>
    </Fragment>
  );
};
export { InventoriesCard };
