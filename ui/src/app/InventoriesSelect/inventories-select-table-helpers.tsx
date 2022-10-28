import React, { useContext } from 'react';
import InventoriesSelectTableContext from '@app/InventoriesSelect/inventories-select-table-context';
import { Radio } from '@patternfly/react-core';
import PropTypes from 'prop-types';

export const SelectRadio = ({ id, label, description }) => {
  const { selectedInventory, setSelectedInventory } = useContext(InventoriesSelectTableContext);
  return (
    <Radio
      id={`select-inventory-${id}`}
      name={`select-inventory-${id}`}
      label={label}
      description={description || label}
      isChecked={selectedInventory?.id === id}
      onChange={() => (setSelectedInventory ? setSelectedInventory({ id: id, name: label }) : undefined)}
    />
  );
};

SelectRadio.propTypes = {
  id: PropTypes.string.isRequired,
};

export const createRows = (data) => {
  return data.map(({ id, name }) => ({
    id,
    cells: [
      <React.Fragment key={`${id}-radio`}>
        <SelectRadio id={id} label={name} description={name} />
      </React.Fragment>,
    ],
  }));
};
