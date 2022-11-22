import React, { Fragment } from 'react';
import { Link } from 'react-router-dom';
import { Text, TextVariants } from '@patternfly/react-core';

export const createRows = (data) =>
  data.map(({ name, rule, rule_id, ruleset, ruleset_id, last_fired_at }) => ({
    cells: [
      name,
      <Fragment key={`[audit-rule-${rule_id}`}>
        <Link
          to={{
            pathname: `/rule/${rule_id}`,
          }}
        >
          {rule || rule_id}
        </Link>
      </Fragment>,
      <Fragment key={`[audit-ruleset-${ruleset}`}>
        <Link
          to={{
            pathname: `/ruleset/${ruleset}`,
          }}
        >
          {ruleset || ruleset_id}
        </Link>
      </Fragment>,
      <Fragment key={`[audit-last_fired-${name}`}>
        <Text component={TextVariants.small}>
          {new Intl.DateTimeFormat('en-US', { dateStyle: 'short', timeStyle: 'long' }).format(
            new Date(last_fired_at || 0)
          )}
        </Text>
      </Fragment>,
    ],
  }));
