import React, { Fragment } from 'react';
import { statusLabel } from '@app/utils/utils';

export const createRows = (data, intl) => {
  return data.map(({ name, status }) => ({
    cells: [name, <Fragment key={`[actions-rule-hosts-${name}`}>{statusLabel({ text: status, intl: intl })}</Fragment>],
  }));
};
