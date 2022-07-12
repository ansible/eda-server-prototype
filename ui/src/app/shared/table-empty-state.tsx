import React, { ReactNode } from 'react';
import PropTypes from 'prop-types';
import {
  EmptyStateIcon,
  EmptyStateBody,
  EmptyStateSecondaryActions,
  Text,
  TextContent,
  TextVariants,
  EmptyState
} from '@patternfly/react-core';
import {EmptyTable} from "@redhat-cloud-services/frontend-components";

export interface TableEmptyState {
  title: ReactNode;
  Icon: React.ComponentType;
  description: ReactNode;
  PrimaryAction?: React.ElementType;
  renderDescription?: () => ReactNode;
}
const TableEmptyState: React.ComponentType<TableEmptyState> = ({
  title,
  Icon,
  description,
  PrimaryAction,
  renderDescription
}) => (
  <EmptyTable centered aria-label="No records">
    <EmptyState className="pf-u-ml-auto pf-u-mr-auto">
      <EmptyStateIcon icon={Icon} />
      <TextContent>
        <Text component={TextVariants.h1}>{title}</Text>
      </TextContent>
      <EmptyStateBody>
        {description}
        {renderDescription && renderDescription()}
      </EmptyStateBody>
      <EmptyStateSecondaryActions>
        {PrimaryAction && <PrimaryAction />}
      </EmptyStateSecondaryActions>
    </EmptyState>
  </EmptyTable>
);

TableEmptyState.propTypes = {
  title: PropTypes.string.isRequired,
  Icon: PropTypes.any.isRequired,
  description: PropTypes.string.isRequired,
  PrimaryAction: PropTypes.any,
  renderDescription: PropTypes.func
};

export default TableEmptyState;
