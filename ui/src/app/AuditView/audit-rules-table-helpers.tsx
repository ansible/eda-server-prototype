import React, { Fragment } from 'react';
import { Link } from 'react-router-dom';
import { Text, TextVariants } from '@patternfly/react-core';

export const createRows = (data) =>
  data.map(({ rule, job, status, ruleset, fired_date }) => ({
    rule,
    cells: [
      <Fragment key={`[audit-rule-${rule?.id}`}>
        <Link
          to={{
            pathname: `/rule/${rule?.id}`,
          }}
        >
          {rule?.name || rule?.id}
        </Link>
      </Fragment>,
      <Fragment key={`[audit-job-${job?.id}`}>
        <Link
          to={{
            pathname: `/job/${job?.id}`,
          }}
        >
          {job?.name || job?.id}
        </Link>
      </Fragment>,
      status,
      <Fragment key={`[audit-ruleset-${ruleset?.id}`}>
        <Link
          to={{
            pathname: `/ruleset/${ruleset?.id}`,
          }}
        >
          {ruleset?.name || ruleset?.id}
        </Link>
      </Fragment>,
      <Fragment key={`[audit-last_fired-${rule?.id}`}>
        <Text component={TextVariants.small}>
          {new Intl.DateTimeFormat('en-US', { dateStyle: 'short', timeStyle: 'long' }).format(
            new Date(fired_date || 0)
          )}
        </Text>
      </Fragment>,
    ],
  }));
