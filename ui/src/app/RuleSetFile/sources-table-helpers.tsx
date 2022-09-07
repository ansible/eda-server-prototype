import React, { Fragment } from 'react';
import {Link} from "react-router-dom";

export const createRows = (data) =>
  data.map(({ id, name, type }) => ({
    id,
    cells: [
      <Fragment key={`[sources-${id}`}>
        <Link
          to={{
            pathname: `/sources/${id}`
          }}
        >
          {name || id}
        </Link>
      </Fragment>,
      type
    ]
  }));
