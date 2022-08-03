import React, { Fragment, useContext } from 'react';
import {Link} from "react-router-dom";

export const createRows = (data) =>
  data.map(({ id, name, status, status, rule, last_fired_at }) => ({
    id,
    cells: [
      <Fragment key={`[job-${id}`}>
        <Link
          to={{
            pathname: `/job/${id}`
          }}
        >
          {name || id}
        </Link>
      </Fragment>,
      status,
      rule,
      last_fired_at
    ]
  }));
