import React, { Fragment } from 'react';
import { Link } from 'react-router-dom';
import {Text, TextVariants} from "@patternfly/react-core";

export const createRows = (data) =>
  data.map(({ id, name, increment_counter, source_type, timestamp }) => ({
    id,
    cells: [
      <Fragment key={`[event-${id}`}>
        <Link
          to={{
            pathname: `/event/${id}`,
          }}
        >
          {name || id}
        </Link>
      </Fragment>,
      increment_counter,
      source_type,
      <Fragment key={`[audit-rule-${id}-event`}>
        <Text component={TextVariants.small}>
          {new Intl.DateTimeFormat('en-US', { dateStyle: 'short', timeStyle: 'long' }).format(
            new Date(timestamp || 0)
          )}
        </Text>
      </Fragment>,
    ],
  }));
