import React, { Fragment } from 'react';
import { Link } from 'react-router-dom';
import { statusLabel } from '@app/utils/utils';

export const createRows = (data, intl) =>
  data.map(({ id, name, status, last_fired_date }) => ({
    id,
    cells: [
      <Fragment key={`[job-${id}`}>
        <Link
          to={{
            pathname: `/job/${id}`,
          }}
        >
          {name || id}
        </Link>
      </Fragment>,
      <Fragment key={`[actions-rule-jobs-${name}`}>{statusLabel({ text: status, intl: intl })}</Fragment>,
      last_fired_date,
    ],
  }));
