import React from 'react';
import PropTypes from 'prop-types';
import { NavLink } from 'react-router-dom';
import { Breadcrumb, BreadcrumbItem } from '@patternfly/react-core';

const Breadcrumbs = ({ breadcrumbs }) => {
  return breadcrumbs ? (
    <Breadcrumb>
      {breadcrumbs.map(({ to, id, title }, idx) => (
        <BreadcrumbItem key={'title'} isActive={idx === breadcrumbs.length - 1} id={id} title={title}>
          {(to && (
            <NavLink isActive={() => false} exact to={to}>
              {title}
            </NavLink>
          )) ||
            title}
        </BreadcrumbItem>
      ))}
    </Breadcrumb>
  ) : null;
};

Breadcrumbs.propTypes = {
  breadcrumbs: PropTypes.arrayOf(
    PropTypes.shape({
      title: PropTypes.string.isRequired,
      to: PropTypes.string,
    })
  ),
};

export default Breadcrumbs;
