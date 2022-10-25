import React, { Fragment } from 'react';
import { Link } from 'react-router-dom';

//TODO - replace the link to the ruleset when the endpoint is updated with that data
export const createRows = (data) => {
  return data.map(({ id, name, rules, fire_count, last_fired_at }) => ({
    id,
    cells: [
      <Fragment key={`[ruleset-${id}`}>
        <Link
          to={{
            pathname: `/rulesets`,
          }}
        >
          {name || id}
        </Link>
      </Fragment>,
      rules ? rules.length : 0,
      fire_count,
      last_fired_at,
    ],
  }));
};
