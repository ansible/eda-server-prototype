import React, { Fragment } from 'react';
import {Link} from "react-router-dom";

export const createRows = (data) =>
  data.map(({ id, name, rules_count, fire_count }) => ({
    id,
    cells: [
      <Fragment key={`[rule-set-${id}`}>
        <Link
          to={{
            pathname: `/rulesetfile/${id}`
          }}
        >
          {name}
        </Link>
      </Fragment>,
      rules_count,
      fire_count
    ]
  }));
