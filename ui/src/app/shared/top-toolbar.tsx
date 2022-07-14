import React, { Fragment } from 'react';
import PropTypes from 'prop-types';
import {
  Level,
  LevelItem,
  PageSection,
  PageSectionVariants,
  Text,
  TextContent, Title,
} from '@patternfly/react-core';
import Breadcrumbs from './breadcrumbs';

export const TopToolbar = ({ children, breadcrumbs }) => (
  <PageSection variant={PageSectionVariants.light}
  >
    {breadcrumbs && (
      <Level className="pf-u-mb-md">
        <Breadcrumbs breadcrumbs={breadcrumbs} />
      </Level>
    )}
    {children}
  </PageSection>
);

TopToolbar.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node
  ]).isRequired,
  breadcrumbs: PropTypes.array,
  paddingBottom: PropTypes.bool,
  className: PropTypes.string
};

TopToolbar.defaultProps = {
  paddingBottom: false
};

export const TopToolbarTitle = ({ title, description, children }) => (
  <Fragment>
    <Level>
      <LevelItem>
        <Title headingLevel={"h2"}>{`${title}`}</Title>
        {description && (
          <TextContent className="pf-u-pt-sm pf-u-mb-md">
            <Text component={TextVariants.p}>{description}</Text>
          </TextContent>
        )}
      </LevelItem>
      {children}
    </Level>
  </Fragment>
);

TopToolbarTitle.propTypes = {
  title: PropTypes.string,
  description: PropTypes.string,
  children: PropTypes.oneOfType([
    PropTypes.node,
    PropTypes.arrayOf(PropTypes.node)
  ])
};
