import React, { Fragment } from 'react';
import { Link } from 'react-router-dom';
import {Text, TextVariants} from "@patternfly/react-core";

export const createRows = (data) =>
  data.map(({ id, name, increment_counter, type, timestamp }) => ({
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
      type,
      <Fragment key={`[actions-rule-${id}-event`}>
        <Text component={TextVariants.small}>
          {new Intl.DateTimeFormat('en-US', { dateStyle: 'short', timeStyle: 'long' }).format(
            new Date(timestamp || 0)
          )}
        </Text>
      </Fragment>,
    ],
  }));
