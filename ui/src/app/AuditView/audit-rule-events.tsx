import { Button, PageSection } from '@patternfly/react-core';
import React, { useEffect, useReducer, useState } from 'react';
import { TableToolbarView } from '@app/shared/table-toolbar-view';
import sharedMessages from '../messages/shared.messages';
import TableEmptyState from '@app/shared/table-empty-state';
import { useIntl } from 'react-intl';
import { defaultSettings } from '@app/shared/pagination';
import { createRows } from './audit-rule-events-table-helpers';
import { CubesIcon } from '@patternfly/react-icons';
import {listAuditRuleEvents} from '@app/API/Audit';
import {RuleType} from "@app/Rules/Rules";
import {renderAuditRuleTabs} from "@app/AuditView/AuditRule";

export interface EventType {
  name: string;
  increment_counter?: string;
  source_type?: string;
  time_stamp?: string;
}

const columns = (intl) => [
  {
    title: intl.formatMessage(sharedMessages.name),
  },
  {
    title: intl.formatMessage(sharedMessages.increment_counter),
  },
  {
    title: intl.formatMessage(sharedMessages.source_type),
  },
  {
    title: intl.formatMessage(sharedMessages.timestamp),
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

const initialState = (filterValue = '') => ({
  filterValue,
  isFetching: false,
  isFiltering: false,
  rows: [],
});

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const eventsListState = (state, action) => {
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

const AuditRuleEvents: React.FunctionComponent<{ rule: RuleType }> = ({ rule }) => {
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);
  const [events, setEvents] = useState<EventType[]>([]);

  const meta = { count: events?.length || 0, limit, offset };
  const [{ filterValue, isFetching, isFiltering, rows }, stateDispatch] = useReducer(eventsListState, initialState());

  const intl = useIntl();
  const updateEvents = (pagination) => {
    stateDispatch({ type: 'setFetching', payload: true });
    return listAuditRuleEvents(rule?.id, pagination)
      .then(() => stateDispatch({ type: 'setFetching', payload: false }))
      .catch(() => stateDispatch({ type: 'setFetching', payload: false }));
  };

  useEffect(() => {
    updateEvents(defaultSettings);
  }, []);

  useEffect(() => {
    stateDispatch({ type: 'setRows', payload: createRows(events) });
  }, [events]);

  const clearFilters = () => {
    stateDispatch({ type: 'clearFilters' });
    return updateEvents(meta);
  };

  const handleFilterChange = (value) => {
    !value || value === '' ? clearFilters() : stateDispatch({ type: 'setFilterValue', payload: value });
  };

  return (
    <PageSection page-type={'audit-rule-events'} id={'audit-rule-events'}>
      {renderAuditRuleTabs(rule?.id, intl)}
      <TableToolbarView
        ouiaId={'audit-rule-events-table'}
        rows={rows}
        setLimit={setLimit}
        setOffset={setOffset}
        columns={columns(intl)}
        fetchData={updateEvents}
        pagination={defaultSettings}
        plural={intl.formatMessage(sharedMessages.events)}
        singular={intl.formatMessage(sharedMessages.event)}
        isLoading={isFetching || isFiltering}
        onFilterChange={handleFilterChange}
        renderEmptyState={() => (
          <TableEmptyState
            title={intl.formatMessage(sharedMessages.noauditruleevents)}
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
                ? intl.formatMessage(sharedMessages.noauditruleevents)
                : intl.formatMessage(sharedMessages.clearAllFiltersDescription)
            }
          />
        )}
      />
    </PageSection>
  );
};

export { AuditRuleEvents };
