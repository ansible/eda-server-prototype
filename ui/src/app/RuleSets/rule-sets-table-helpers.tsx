import React, { Fragment } from 'react';
import { Link } from 'react-router-dom';

export const createRows = (data) =>
  data.map(({ id, name, rule_count }) => ({
    id,
    cells: [
      <Fragment key={`[rule-set-${id}`}>
        <Link
          to={{
            pathname: `/ruleset/${id}`,
          }}
        >
          {name}
        </Link>
      </Fragment>,
      rule_count,
    ],
  }));
