import React, { Fragment } from 'react';
import {Link} from "react-router-dom";

export const createRows = (data) =>
  data.map(({ id, name, status,  number_of_rules, fire_count}) => ({
    id,
    cells: [
      <Fragment key={`[rule-${id}`}>
        <Link
          to={{
            pathname: `/rule/${id}`
          }}
        >
          {name}
        </Link>
      </Fragment>,
      status,
      number_of_rules,
      fire_count
    ]
  }));
