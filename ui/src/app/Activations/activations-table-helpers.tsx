import React, {Fragment, useContext} from 'react';
import {Link} from "react-router-dom";
import ActivationsTableContext from "@app/Activations/activations-table-context";
import {Checkbox} from "@patternfly/react-core";
import PropTypes from "prop-types";
import {ActivationType} from "@app/Activations/Activations";

export const SelectBox = ({ id }) => {
  const {
    selectedActivations,
    setSelectedActivations
  } = useContext(ActivationsTableContext);

  return (
    <Checkbox
      id={`select-${id}`}
      isChecked={selectedActivations.includes(id)}
      onChange={() => setSelectedActivations ? setSelectedActivations(id) : ''}
    />
  );
};

SelectBox.propTypes = {
  id: PropTypes.string.isRequired
};

export const createRows = (data: ActivationType[]) =>
  data.map(({ id, name, status,  number_of_rules, fire_count}) => ({
    id,
    cells: [
      <React.Fragment key={`${id}-checkbox`}>
        <SelectBox id={id} />
      </React.Fragment>,
      <Fragment key={`[activation-${id}`}>
        <Link
          to={{
            pathname: `/activation/${id}`
          }}
        >
          {name}
        </Link>
      </Fragment>,
      status,
      number_of_rules,
      fire_count
    ]
  }));
