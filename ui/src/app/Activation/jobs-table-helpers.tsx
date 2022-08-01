import React, { Fragment, useContext } from 'react';
import {Link} from "react-router-dom";

export const createRows = (data) =>
  data.map(({ id, name }) => ({
    id,
    cells: [
      <Fragment key={`[job-${id}`}>
        <Link
          to={{
            pathname: `/job/${id}`
          }}
        >
          {name}
        </Link>
      </Fragment>
    ]
  }));
