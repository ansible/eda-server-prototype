import React, { Fragment, useContext } from 'react';
import PropTypes from 'prop-types';
import { Checkbox } from '@patternfly/react-core';
import ActivationsTableContext from './activations-table-context';
import {Link} from "react-router-dom";

export const SelectBox = ({ id }) => {
  const {
    selectedActivations,
    setSelectedActivations
  } = useContext(ActivationsTableContext);

  return (
    <Checkbox
      id={`select-${id}`}
      isChecked={selectedActivations.includes(id)}
      onChange={() => setSelectedActivations(id)}
    />
  );
};

SelectBox.propTypes = {
  id: PropTypes.string.isRequired
};

export const createRows = (data) =>
  data.map(({ id, name }) => ({
    id,
    cells: [
      <React.Fragment key={`${id}-checkbox`}>
        <SelectBox id={id} />
      </React.Fragment>,
      <Fragment key={`[activation-${id}`}>
        <Link
          to={{
            pathname: `/activation/${id}/details`
          }}
        >
          {name}
        </Link>
      </Fragment>
    ]
  }));
