import React, { Fragment } from 'react';
import { Link } from 'react-router-dom';

//TODO - replace the link to the ruleset when the endpoint is updated with that data
export const createRows = (data) => {
  console.log('Debug - createRows data: ', data);
  return data.map(({ id, name, rule_count, fired_stats }) => ({
    id,
    cells: [
      <Fragment key={`[ruleset-${id}`}>
        <Link
          to={{
            pathname: `/ruleset/${id}`,
          }}
        >
          {name || id}
        </Link>
      </Fragment>,
      rule_count,
      fired_stats?.fired_count,
      fired_stats?.last_fired_at,
    ],
  }));
};
