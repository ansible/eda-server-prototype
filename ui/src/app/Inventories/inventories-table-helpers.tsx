import React, {Fragment, useContext} from 'react';
import {Link} from "react-router-dom";
import InventoriesTableContext from "@app/Inventories/inventories-table-context";
import {Checkbox} from "@patternfly/react-core";
import PropTypes from "prop-types";

export const SelectBox = ({ id }) => {
  const {
    selectedInventories,
    setSelectedInventories
  } = useContext(InventoriesTableContext);

  return (
    <Checkbox
      id={`select-${id}`}
      isChecked={selectedInventories.includes(id)}
      onChange={() => setSelectedInventories ? setSelectedInventories(id) : ''}
    />
  );
};

SelectBox.propTypes = {
  id: PropTypes.string.isRequired
};

export const createRows = (data) =>
  data.map(({ id, name, source}) => ({
    id,
    cells: [
      <React.Fragment key={`${id}-checkbox`}>
        <SelectBox id={id} />
      </React.Fragment>,
      <Fragment key={`[inventory-${id}`}>
        <Link
          to={{
            pathname: `/inventories/inventory/${id}`
          }}
        >
          {name}
        </Link>
      </Fragment>,
      source
    ]
  }));
