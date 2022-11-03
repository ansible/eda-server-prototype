import React, { Fragment, useContext } from 'react';
import PropTypes from 'prop-types';
import { Checkbox } from '@patternfly/react-core';
import JobsTableContext from './jobs-table-context';
import { Link } from 'react-router-dom';

export const SelectBox = ({ id }) => {
  const { selectedJobs, setSelectedJobs } = useContext(JobsTableContext);

  return (
    <Checkbox
      id={`select-${id}`}
      isChecked={selectedJobs.includes(id)}
      onChange={() => (setSelectedJobs ? setSelectedJobs(id) : '')}
    />
  );
};

SelectBox.propTypes = {
  id: PropTypes.string.isRequired,
};

export const createRows = (data) =>
  data.map(({ id }) => ({
    id,
    cells: [
      <React.Fragment key={`${id}-checkbox`}>
        <SelectBox id={id} />
      </React.Fragment>,
      <Fragment key={`[job-${id}`}>
        <Link
          to={{
            pathname: `/job/${id}`,
          }}
        >
          {id}
        </Link>
      </Fragment>,
    ],
  }));
