import React, { Fragment } from 'react';
import { Link } from 'react-router-dom';
import { Text, TextVariants } from '@patternfly/react-core';
import {statusLabel} from "@app/utils/utils";

export const createRows = (data, intl) =>
  data.map(({ rule, type, status, ruleset, fired_date }) => ({
    rule,
    cells: [
      <Fragment key={`[actions-rule-${rule?.id}`}>
        <Link
          to={{
            pathname: `/actions-rule/${rule?.id}`,
          }}
        >
          {rule?.name || rule?.id}
        </Link>
      </Fragment>,
      type,
      <Fragment key={`[actions-rule-${rule?.id}-status`}>{statusLabel({ text: status, intl: intl })}</Fragment>,
      <Fragment key={`[actions-ruleset-${ruleset?.id}`}>
        <Link
          to={{
            pathname: `/ruleset/${ruleset?.id}`,
          }}
        >
          {ruleset?.name || ruleset?.id}
        </Link>
      </Fragment>,
      <Fragment key={`[actions-last_fired-${rule?.id}`}>
        <Text component={TextVariants.small}>
          {new Intl.DateTimeFormat('en-US', { dateStyle: 'short', timeStyle: 'long' }).format(
            new Date(fired_date || 0)
          )}
        </Text>
      </Fragment>,
    ],
  }));
