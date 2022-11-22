import React, { Fragment } from 'react';
import { Link } from 'react-router-dom';

export const createRows = (data) =>
  data.map(({ name, rule, rule_name, ruleset, ruleset_name, last_fired_at }) => ({
    cells: [
      name,
      <Fragment key={`[audit-rule-${rule}`}>
        <Link
          to={{
            pathname: `/rules/${rule}`,
          }}
        >
          {rule_name || rule}
        </Link>
      </Fragment>,
      <Fragment key={`[audit-ruleset-${ruleset}`}>
        <Link
          to={{
            pathname: `/ruleset/${ruleset}`,
          }}
        >
          {ruleset_name || ruleset}
        </Link>
      </Fragment>,
      last_fired_at,
    ],
  }));
