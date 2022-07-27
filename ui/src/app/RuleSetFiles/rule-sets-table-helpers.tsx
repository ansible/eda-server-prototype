import React, { Fragment } from 'react';
import {Link} from "react-router-dom";

export const createRows = (data) =>
  data.map(({ id, name }) => ({
    id,
    cells: [
      <Fragment key={`[rule-set-${id}`}>
        <Link
          to={{
            pathname: `/rule-set-file/${id}`
          }}
        >
          {name}
        </Link>
      </Fragment>
    ]
  }));
