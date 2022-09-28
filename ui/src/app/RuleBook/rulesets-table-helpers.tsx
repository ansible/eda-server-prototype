import React, { Fragment } from 'react';
import {Link} from "react-router-dom";

export const createRows = (data) => {
  console.log('Debug create rule row - data: ', data);
  return data.map(({id, name, condition, action, fire_count, last_fired_at}) => ({
    id,
    cells: [
      <Fragment key={`[rule-${id}`}>
        <Link
          to={{
            pathname: `/rule/${id}`
          }}
        >
          {name || id}
        </Link>
      </Fragment>,
      condition,
      `${(Object.keys(action))}`,
      fire_count,
      last_fired_at
    ]
  }));
}
