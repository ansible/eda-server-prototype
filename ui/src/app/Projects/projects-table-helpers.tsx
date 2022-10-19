import React, { Fragment, useContext } from 'react';
import PropTypes from 'prop-types';
import { Checkbox } from '@patternfly/react-core';
import ProjectsTableContext from './projects-table-context';
import {Link} from "react-router-dom";
import {ProjectType} from "@app/shared/types/common-types";

export const SelectBox = ({ id }) => {
  const {
    selectedProjects,
    setSelectedProjects
  } = useContext(ProjectsTableContext);

  return (
    <Checkbox
      id={`select-${id}`}
      isChecked={selectedProjects.includes(id)}
      onChange={() => setSelectedProjects ? setSelectedProjects(id) : ''}
    />
  );
};

SelectBox.propTypes = {
  id: PropTypes.string.isRequired
};

export const createRows = (data: ProjectType[]) =>
  data.map(({ id, name, status, type, revision }) => ({
    id,
    cells: [
      <React.Fragment key={`${id}-checkbox`}>
        <SelectBox id={id} />
      </React.Fragment>,
      <Fragment key={`[project-${id}`}>
        <Link
          to={{
            pathname: `/project/${id}`
          }}
        >
          {name}
        </Link>
      </Fragment>,
      status,
      type,
      revision || '000000'
    ]
  }));
