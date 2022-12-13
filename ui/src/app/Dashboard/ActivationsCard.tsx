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
import { listActivations } from '@app/API/Activation';

interface ActivationCardType {
  id: string;
  name: string;
  status?: string;
  revision?: string;
}

const createRows = (data: ActivationCardType[]) =>
  data.slice(-4).map(({ id, name, status }) => ({
    id,
    cells: [
      <Fragment key={`[activation-${id}`}>
        <Link
          to={{
            pathname: `/activation/${id}`,
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
    title: intl.formatMessage(sharedMessages.status),
  },
];

const initialState = () => ({
  isFetching: true,
  rows: [],
});

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const activationsListState = (state, action) => {
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

const ActivationsCard: React.FunctionComponent = () => {
  const intl = useIntl();
  const [activations, setActivations] = useState<ActivationCardType[]>([]);
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);
  const [{ isFetching, rows }, stateDispatch] = useReducer(activationsListState, initialState());
  const history = useHistory();

  const updateRows = () => {
    stateDispatch({ type: 'setFetching', payload: true });
    return listActivations()
      .then((data) => {
        setActivations(data?.data);
        stateDispatch({ type: 'setRows', payload: createRows(activations) });
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
    stateDispatch({ type: 'setRows', payload: createRows(activations) });
  }, [activations]);

  return (
    <Fragment>
      <Card style={{ transition: 'box-shadow 0.25s', minHeight: 575 }}>
        <CardTitle>
          <Level>
            <LevelItem>
              <Title headingLevel={'h2'}>{intl.formatMessage(sharedMessages.activations)}</Title>
            </LevelItem>
            <LevelItem>
              <Button variant="link" onClick={() => history.push('/activations')}>
                {intl.formatMessage(sharedMessages.go_to_activations)}
              </Button>
            </LevelItem>
          </Level>
        </CardTitle>
        <CardBody isFilled={true}>
          <TableToolbarView
            ouiaId={'activations-table'}
            rows={rows}
            setLimit={setLimit}
            setOffset={setOffset}
            columns={columns(intl)}
            fetchData={updateRows}
            plural={intl.formatMessage(sharedMessages.activations)}
            singular={intl.formatMessage(sharedMessages.activation)}
            isLoading={isFetching}
            renderEmptyState={() => (
              <TableEmptyState
                title={intl.formatMessage(sharedMessages.noactivations_description)}
                Icon={PlusCircleIcon}
                PrimaryAction={() => (
                  <Link id="create-activation-link" to={{ pathname: '/new-activation' }}>
                    <Button
                      ouiaId={'create-activation-link'}
                      variant="primary"
                      aria-label={intl.formatMessage(sharedMessages.addActivation)}
                    >
                      {intl.formatMessage(sharedMessages.addActivation)}
                    </Button>
                  </Link>
                )}
                description={intl.formatMessage(sharedMessages.noactivations_action)}
              />
            )}
          />
        </CardBody>
        <CardFooter>
          <Button variant="link" icon={<PlusCircleIcon />} onClick={() => history.push('/new-activation')}>
            {intl.formatMessage(sharedMessages.create_activation)}
          </Button>
        </CardFooter>
      </Card>
    </Fragment>
  );
};
export { ActivationsCard };
