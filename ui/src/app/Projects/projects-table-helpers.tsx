import React, { useContext } from 'react';
import PropTypes from 'prop-types';
import { Checkbox } from '@patternfly/react-core';
import ProjectsTableContext from './projects-table-context';

export const SelectBox = ({ id }) => {
  const {
    selectedProjects,
    setSelectedProjects
  } = useContext(ProjectsTableContext);

  return (
    <Checkbox
      id={`select-${id}`}
      isChecked={selectedProjects.includes(id)}
      onChange={() => setSelectedProjects(id)}
    />
  );
};

SelectBox.propTypes = {
  id: PropTypes.string.isRequired
};

export const createRows = (data) =>
  data.map(({ id, url }) => ({
    id,
    cells: [
      <React.Fragment key={`${id}-checkbox`}>
        <SelectBox id={id} />
      </React.Fragment>,
      url
    ]
  }));
