/* eslint-disable react/prop-types */
import React, {Fragment, ReactNode, SetStateAction} from 'react';
import {
  Table,
  TableHeader,
  TableBody,
  IActionsResolver,
  ISortBy,
  OnSort,
  IRow,
  ICell
} from '@patternfly/react-table';
import {
  defaultSettings,
  getCurrentPage,
  getNewPage,
  PaginationConfiguration
} from '../shared/pagination';
import { useIntl } from 'react-intl';
import {
  PrimaryToolbar
} from '@redhat-cloud-services/frontend-components/PrimaryToolbar';
import sharedMessages from '../messages/shared.messages';

export interface TableToolbarViewProps {
  columns: ICell[];
  toolbarButtons?: () => ReactNode;
  fetchData: (pagination: PaginationConfiguration) => Promise<any | void>;
  setLimit: any,
  setOffset: any,
  pagination?: PaginationConfiguration;
  plural?: string;
  singular?: string;
  routes?: () => ReactNode;
  actionResolver?: IActionsResolver;
  filterValue?: string;
  onFilterChange: (value?: string) => void;
  isLoading?: boolean;
  renderEmptyState?: () => ReactNode;
  sortBy?: ISortBy;
  onSort?: OnSort;
  rows: IRow[];
  ouiaId?: string;
}
export const TableToolbarView: React.ComponentType<TableToolbarViewProps> = ({
  columns,
  fetchData,
  toolbarButtons,
  actionResolver,
  routes = () => null,
  setLimit,
  setOffset,
  plural,
  pagination = defaultSettings,
  filterValue,
  onFilterChange,
  isLoading = false,
  renderEmptyState = () => null,
  sortBy,
  onSort,
  rows,
  ouiaId
}) => {
  const intl = useIntl();

  const paginationConfig = {
    itemCount: pagination.count,
    page: pagination.offset || 1,
    perPage: pagination.limit,
    onSetPage: (_e, page) => {
      setOffset(page || 1);
      return fetchData({ ...pagination, offset: page });
    },
    onPerPageSelect: (_e, size) => {
      setLimit(size);
      return fetchData({ ...pagination, limit: size });
    },
    isDisabled: isLoading
  };

  const renderToolbar = () => (
    <PrimaryToolbar
      pagination={paginationConfig}
      {...(toolbarButtons && {
        actionsConfig: {
          dropdownProps: {
            position: 'right'
          },
          actions: [toolbarButtons()]
        }
      })}
      filterConfig={{
        items: [
          {
            label: intl.formatMessage({
              id: 'search',
              defaultMessage: 'Search'
            }),
            filterValues: {
              id: 'search',
              placeholder: intl.formatMessage(
                sharedMessages.search
              ),
              'aria-label': intl.formatMessage(
                sharedMessages.search
              ),
              onChange: (
                _event: React.SyntheticEvent<Element, Event>,
                value?: string
              ) => onFilterChange(value),
              value: filterValue
            }
          }
        ]
      }}
    />
  );
  console.log('Debug tableToolbarView - rows: ', rows);
  console.log('Debug tableToolbarView - routes: ', routes());
  return (
    <Fragment>
      {!isLoading && rows.length === 0 ? (
        renderEmptyState()
      ) : (
        <Fragment>
          {routes()}
          {renderToolbar()}
          {!isLoading && (
            <Table
              aria-label={`${plural} table`}
              rows={rows}
              cells={columns}
              actionResolver={actionResolver}
              className="pf-u-pt-0"
              sortBy={sortBy}
              onSort={onSort}
              ouiaId={ouiaId}
            >
              <TableHeader />
              <TableBody />
            </Table>
          )}
          {pagination.count! > 0 && (
            <PrimaryToolbar
              pagination={{
                ...paginationConfig,
                dropDirection: 'up',
                variant: 'bottom',
                isCompact: false,
                className: 'pf-u-pr-0'
              }}
            />
          )}
        </Fragment>
      )}
    </Fragment>
  );
};
