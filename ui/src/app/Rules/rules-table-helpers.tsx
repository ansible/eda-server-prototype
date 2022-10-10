import React, { Fragment } from 'react';
import {Link} from "react-router-dom";

export const createRows = (data) =>
  data.map(({ id, name, ruleset, action, last_fired_at}) => ({
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
      <Fragment key={`[ruleset-${id}`}>
        <Link
          to={{
            pathname: `/ruleset/${ruleset?.id}`
          }}
        >
          {ruleset?.name || `Ruleset ${ruleset?.id}`}
        </Link>
      </Fragment>,
      action,
      last_fired_at
    ]
  }));
