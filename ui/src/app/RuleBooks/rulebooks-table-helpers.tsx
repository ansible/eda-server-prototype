import React, { Fragment } from 'react';
import { Link } from 'react-router-dom';

export const createRows = (data) =>
  data.map(({ id, name, ruleset_count, fire_count }) => ({
    id,
    cells: [
      <Fragment key={`[rule-book-${id}`}>
        <Link
          to={{
            pathname: `/rulebooks/rulebook/${id}`,
          }}
        >
          {name}
        </Link>
      </Fragment>,
      ruleset_count,
      fire_count,
    ],
  }));
