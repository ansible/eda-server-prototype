import React, { Fragment } from 'react';
import {Link} from "react-router-dom";

export const createRows = (data) =>
  data.map(({ id, name }) => ({
    id,
    cells: [
      <Fragment key={`[activation-${id}`}>
        <Link
          to={{
            pathname: `/activation/${id}`
          }}
        >
          {name}
        </Link>
      </Fragment>
    ]
  }));
