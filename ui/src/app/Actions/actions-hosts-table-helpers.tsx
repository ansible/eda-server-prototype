import React, { Fragment } from 'react';
import { Link } from 'react-router-dom';
import { Text, TextVariants } from '@patternfly/react-core';

export const createRows = (data) =>
  data.map(({ host, rule, ruleset, fired_date }) => ({
    cells: [
      host,
      <Fragment key={`[actions-host-${rule?.id}`}>
        <Link
          to={{
            pathname: `/rule/${rule?.id}`,
          }}
        >
          {rule?.name || rule?.id}
        </Link>
      </Fragment>,
      <Fragment key={`[actions-ruleset-${ruleset?.id}`}>
        <Link
          to={{
            pathname: `/ruleset/${ruleset?.id}`,
          }}
        >
          {ruleset?.name || ruleset?.id}
        </Link>
      </Fragment>,
      <Fragment key={`[actions-last_fired-${rule?.name}`}>
        <Text component={TextVariants.small}>
          {new Intl.DateTimeFormat('en-US', { dateStyle: 'short', timeStyle: 'long' }).format(
            new Date(fired_date || 0)
          )}
        </Text>
      </Fragment>,
    ],
  }));
