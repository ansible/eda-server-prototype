import React, { Fragment } from 'react';
import {Link} from "react-router-dom";

export const createRows = (data) =>
  data.map(({ id, url }) => ({
    id,
    cells: [
      <Fragment key={`[project-${id}`}>
        <Link
          to={{
            pathname: `/project/${id}`
          }}
        >
          {url}
        </Link>
      </Fragment>
    ]
  }));
