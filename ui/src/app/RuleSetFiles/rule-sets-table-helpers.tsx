import React, { Fragment, useContext } from 'react';
import PropTypes from 'prop-types';
import { Checkbox } from '@patternfly/react-core';
import RuleSetsTableContext from './rule-sets-table-context';
import {Link} from "react-router-dom";

export const SelectBox = ({ id }) => {
  const {
    selectedRuleSets,
    setSelectedRuleSets
  } = useContext(RuleSetsTableContext);

  return (
    <Checkbox
      id={`select-${id}`}
      isChecked={selectedRuleSets.includes(id)}
      onChange={() => setSelectedRuleSets(id)}
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
      <Fragment key={`[rule-set-${id}`}>
        <Link
          to={{
            pathname: `/rule-set-file/${id}`
          }}
        >
          {name}
        </Link>
      </Fragment>
    ]
  }));
