import React, { Fragment } from 'react';
import {Link} from "react-router-dom";

export const createRows = (data) =>
  data.map(({ id, name, source }) => ({
    id,
    cells: [
      <Fragment key={`[inventory-${id}`}>
        <Link
          to={{
            pathname: `/inventories/inventory/${id}`
          }}
        >
          {name}
        </Link>
      </Fragment>,
      source
    ]
  }));
