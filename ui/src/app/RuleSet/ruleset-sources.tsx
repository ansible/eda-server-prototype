import { Button, PageSection } from '@patternfly/react-core';
import { useHistory, useParams } from 'react-router-dom';
import React, { useEffect, useReducer, useState } from 'react';
import { TableToolbarView } from '@app/shared/table-toolbar-view';
import sharedMessages from '../messages/shared.messages';
import { cellWidth } from '@patternfly/react-table';
import TableEmptyState from '@app/shared/table-empty-state';
import { useIntl } from 'react-intl';
import { defaultSettings } from '@app/shared/pagination';
import { createRows } from './sources-table-helpers';
import { CubesIcon } from '@patternfly/react-icons';
import { renderRuleSetFileTabs, RuleSetType } from '@app/RuleSet/ruleset';
import { SourceType } from '@app/RuleSets/RuleSets';
import {fetchRulesetSources} from "@app/API/Ruleset";

const columns = (intl) => [
  {
    title: intl.formatMessage(sharedMessages.name),
    transforms: [cellWidth(40)],
  },
  {
    title: intl.formatMessage(sharedMessages.type),
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
export const sourcesListState = (state, action) => {
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

const RulesetSources: React.FunctionComponent<{ ruleset: RuleSetType }> = ({ ruleset }) => {
  const history = useHistory();
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);
  const [sources, setSources] = useState<SourceType[]>([]);

  const { id } = useParams<{ id: string }>();

  const meta = { count: sources?.length || 0, limit, offset };
  const [{ filterValue, isFetching, isFiltering, rows }, stateDispatch] = useReducer(sourcesListState, initialState());

  const intl = useIntl();
  const updateSources = (pagination) => {
    stateDispatch({ type: 'setFetching', payload: true });
    return fetchRulesetSources(id, pagination)
      .then((data) => setSources(data?.data))
      .then(() => stateDispatch({ type: 'setFetching', payload: false }))
      .catch(() => stateDispatch({ type: 'setFetching', payload: false }));
  };

  useEffect(() => {
    fetchRulesetSources(id).then((data) => {
      stateDispatch({ type: 'setRows', payload: createRows(data) });
    });
  }, []);

  useEffect(() => {
    updateSources(defaultSettings);
  }, []);

  const clearFilters = () => {
    stateDispatch({ type: 'clearFilters' });
    return updateSources(meta);
  };

  const handleFilterChange = (value) => {
    !value || value === '' ? clearFilters() : stateDispatch({ type: 'setFilterValue', payload: value });
  };

  return (
    <PageSection page-type={'ruleset-sources'} id={'ruleset-sources'}>
      {renderRuleSetFileTabs(id, intl)}
      <TableToolbarView
        ouiaId={'ruleset-sources-table'}
        rows={rows}
        setLimit={setLimit}
        setOffset={setOffset}
        columns={columns(intl)}
        fetchData={updateSources}
        plural={intl.formatMessage(sharedMessages.sources)}
        singular={intl.formatMessage(sharedMessages.sources)}
        isLoading={isFetching || isFiltering}
        onFilterChange={handleFilterChange}
        renderEmptyState={() => (
          <TableEmptyState
            title={intl.formatMessage(sharedMessages.norulesetsources)}
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
                ? intl.formatMessage(sharedMessages.norulesetsources)
                : intl.formatMessage(sharedMessages.clearAllFiltersDescription)
            }
          />
        )}
      />
    </PageSection>
  );
};

export { RulesetSources };
