import React, { Fragment, useContext } from 'react';
import { Link } from 'react-router-dom';
import InventoriesTableContext from '@app/Inventories/inventories-table-context';
import { Checkbox } from '@patternfly/react-core';

interface InventoryType {
  name: string;
  description?: string;
  inventory: string;
  id: string;
  source: string;
}
export const SelectBox = (props: { id: string }): JSX.Element => {
  const { id } = props;
  const { selectedInventories, setSelectedInventories } = useContext(InventoriesTableContext);

  return (
    <Checkbox
      id={`select-${id}`}
      isChecked={selectedInventories.includes(id)}
      onChange={() => (setSelectedInventories ? setSelectedInventories(id) : '')}
    />
  );
};

export const createRows = (data: InventoryType[]): { id: string; cells: React.ReactNode }[] =>
  data.map(({ id, source, name }: InventoryType) => ({
    id,
    cells: [
      <React.Fragment key={`${id}-checkbox`}>
        <SelectBox id={id} />
      </React.Fragment>,
      <Fragment key={`[inventory-${id}`}>
        <Link
          to={{
            pathname: `/inventories/${id}/details`,
          }}
        >
          {name}
        </Link>
      </Fragment>,
      source,
    ],
  }));
