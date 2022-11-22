import React, { Fragment } from 'react';
import { Link } from 'react-router-dom';

export const createRows = (data) =>
  data.map(({ id, name, status, last_fired_at }) => ({
    id,
    cells: [
      <Fragment key={`[job-${id}`}>
        <Link
          to={{
            pathname: `/job/${id}`,
          }}
        >
          {name || id}
        </Link>
      </Fragment>,
      status,
      last_fired_at,
    ],
  }));
