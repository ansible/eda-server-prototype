import { Dropdown, DropdownItem, DropdownPosition, KebabToggle, Level, LevelItem, Title } from '@patternfly/react-core';
import { Link, Route, Switch, useLocation, useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import { useIntl } from 'react-intl';
import AppTabs from '@app/shared/app-tabs';
import { CaretLeftIcon } from '@patternfly/react-icons';
import { getTabFromPath } from '@app/utils/utils';
import { TopToolbar } from '@app/shared/top-toolbar';
import { InventoryDetails } from '@app/Inventory/inventory-details';
import sharedMessages from '../messages/shared.messages';
import { AnyObject } from '@app/shared/types/common-types';
import { fetchInventory } from '@app/API/Inventory';

interface TabItemType {
  eventKey: number;
  title: string | JSX.Element;
  name: string;
}

export interface InventoryType {
  id: string;
  name?: string;
  description?: string;
  inventory?: string;
  source?: string;
  created_at?: string;
  modified_at?: string;
}

const buildInventoryTabs = (inventoryId: string, intl: AnyObject): TabItemType[] => [
  {
    eventKey: 0,
    title: (
      <div>
        <CaretLeftIcon />
        {intl.formatMessage(sharedMessages.backToInventories)}
      </div>
    ),
    name: `/inventories`,
  },
  { eventKey: 1, title: 'Details', name: `/inventories/inventory/${inventoryId}/details` },
];

export const renderInventoryTabs = (inventoryId: string, intl) => {
  const inventory_tabs = buildInventoryTabs(inventoryId, intl);
  return <AppTabs tabItems={inventory_tabs} />;
};

const Inventory: React.FunctionComponent = () => {
  const [inventory, setInventory] = useState<InventoryType | undefined>(undefined);
  const { id } = useParams<{ id: string }>();
  const [isOpen, setOpen] = useState<boolean>(false);
  const intl = useIntl();

  useEffect(() => {
    fetchInventory(id).then((data) => setInventory(data.data));
  }, []);

  const location = useLocation();
  const currentTab = inventory?.id
    ? getTabFromPath(buildInventoryTabs(inventory.id, intl), location.pathname)
    : intl.formatMessage(sharedMessages.details);

  const dropdownItems = [
    <DropdownItem
      aria-label="Edit"
      key="edit-inventory"
      id="edit-inventory"
      component={
        <Link to={`/inventories/inventory/edit-inventory/${id}`}>{intl.formatMessage(sharedMessages.edit)}</Link>
      }
      role="link"
    />,
    <DropdownItem
      aria-label="Delete"
      key="delete-inventory"
      id="delete-inventory"
      component={<Link to={`/inventory/${id}/remove`}>{intl.formatMessage(sharedMessages.delete)}</Link>}
      role="link"
    />,
  ];

  return (
    <React.Fragment>
      <TopToolbar
        breadcrumbs={[
          {
            title: intl.formatMessage(sharedMessages.inventories),
            key: 'inventories',
            to: '/inventories',
          },
          {
            title: inventory?.name,
            key: 'details',
            to: `/inventories/inventory/${inventory?.id}/details`,
          },
          {
            title: currentTab || intl.formatMessage(sharedMessages.details),
            key: 'current_tab',
          },
        ]}
      >
        <Level>
          <LevelItem>
            <Title headingLevel={'h2'}>{`${inventory?.name}`}</Title>
          </LevelItem>
          <LevelItem>
            <Dropdown
              isPlain
              onSelect={() => setOpen(false)}
              position={DropdownPosition.right}
              toggle={<KebabToggle id="rulebook-details-toggle" onToggle={(isOpen) => setOpen(isOpen)} />}
              isOpen={isOpen}
              dropdownItems={dropdownItems}
            />
          </LevelItem>
        </Level>
      </TopToolbar>
      {inventory && (
        <Switch>
          <Route path="/inventories/inventory/:id">
            <InventoryDetails inventory={inventory} />
          </Route>
        </Switch>
      )}
    </React.Fragment>
  );
};

export { Inventory };
