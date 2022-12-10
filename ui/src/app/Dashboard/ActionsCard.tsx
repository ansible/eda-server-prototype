import { Card, CardBody, CardTitle, Title } from '@patternfly/react-core';
import { Link } from 'react-router-dom';
import React, { useState, useEffect, useReducer, Fragment } from 'react';
import { PlusCircleIcon } from '@patternfly/react-icons';
import sharedMessages from '../messages/shared.messages';
import { TableToolbarView } from '@app/shared/table-toolbar-view';
import TableEmptyState from '@app/shared/table-empty-state';
import { useIntl } from 'react-intl';
import { defaultSettings } from '@app/shared/pagination';
import { listActionsRules } from '@app/API/Actions';
import { Text, TextVariants } from '@patternfly/react-core';
import {statusLabel} from "@app/utils/utils";

interface ActionCardType {
  rule: {id: string; name: string;}
  status?: string;
  fired_date?: string;
}

export const createRows = (data, intl) =>
  data.map(({ rule, status, fired_date }) => ({
    rule,
    cells: [
      <Fragment key={`[actions-rule-${rule?.id}`}>
        <Link
          to={{
            pathname: `/actions-rule/${rule?.id}`,
          }}
        >
          {rule?.name || rule?.id}
        </Link>
      </Fragment>,
      <Fragment key={`[actions-rule-${rule?.id}-status`}>{statusLabel({ text: status, intl: intl })}</Fragment>,
      <Fragment key={`[actions-last_fired-${rule?.id}`}>
        <Text component={TextVariants.small}>
          {new Intl.DateTimeFormat('en-US', { dateStyle: 'short', timeStyle: 'long' }).format(
            new Date(fired_date || 0)
          )}
        </Text>
      </Fragment>,
    ],
  }));
const columns = (intl) => [
  {
    title: intl.formatMessage(sharedMessages.name),
  },
  {
    title: intl.formatMessage(sharedMessages.status),
  },

  {
    title: intl.formatMessage(sharedMessages.lastFiredDate),
  },
];

const initialState = () => ({
  isFetching: true,
  rows: [],
});

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const actionsListState = (state, action) => {
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

const ActionsCard: React.FunctionComponent = () => {
  const intl = useIntl();
  const [actions, setActions] = useState<ActionCardType[]>([]);
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);
  const [{ isFetching, rows }, stateDispatch] = useReducer(actionsListState, initialState());

  const updateRows = () => {
    stateDispatch({ type: 'setFetching', payload: true });
    return listActionsRules()
      .then((data) => {
        setActions(data?.data);
        stateDispatch({ type: 'setRows', payload: createRows(actions, intl) });
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
    stateDispatch({ type: 'setRows', payload: createRows(actions, intl) });
  }, [actions]);

  return (
    <Fragment>
      <Card>
        <CardTitle>
          <Title headingLevel={'h2'}>Actions</Title>
        </CardTitle>
        <CardBody>
          <TableToolbarView
            ouiaId={'actions-table'}
            rows={rows}
            setLimit={setLimit}
            setOffset={setOffset}
            columns={columns(intl)}
            fetchData={updateRows}
            plural={intl.formatMessage(sharedMessages.rules)}
            singular={intl.formatMessage(sharedMessages.rule)}
            isLoading={isFetching}
            renderEmptyState={() => (
              <TableEmptyState
                title={intl.formatMessage(sharedMessages.noprojects_description)}
                Icon={PlusCircleIcon}
                PrimaryAction={() => null}
                description={intl.formatMessage(sharedMessages.noprojects_description)}
              />
            )}
          />
        </CardBody>
      </Card>
    </Fragment>
  );
};
export { ActionsCard };
