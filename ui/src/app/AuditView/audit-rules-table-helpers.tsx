import React, { Fragment } from 'react';
import { Link } from 'react-router-dom';

export const createRows = (data) =>
  data.map(({ id, name, job_name, status, ruleset, last_fired_at }) => ({
    id,
    cells: [
      <Fragment key={`[audit-rule-${id}`}>
        <Link
          to={{
            pathname: `/rules/${id}`,
          }}
        >
          {name || id}
        </Link>
      </Fragment>,
      job_name,
      status,
      ruleset.name,
      last_fired_at,
    ],
  }));
