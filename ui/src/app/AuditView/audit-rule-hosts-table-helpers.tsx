import React from 'react';

export const createRows = (data) =>
  data.map(({ name, status }) => ({
    cells: [name, status],
  }));
