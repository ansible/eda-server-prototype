import {Title} from '@patternfly/react-core';
import {Route, Switch, useLocation, useParams} from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import {useIntl} from "react-intl";
import AppTabs from "@app/shared/app-tabs";
import {CaretLeftIcon} from "@patternfly/react-icons";
import {getServer} from "@app/utils/utils";
import {TopToolbar} from "@app/shared/top-toolbar";
import {InventoryDetails} from "@app/Inventory/inventory-details";
import sharedMessages from "../messages/shared.messages";
import {AnyObject} from "@app/shared/types/common-types";

interface TabItemType {
  eventKey: number;
  title: string | JSX.Element;
  name: string;
}

export interface InventoryType {
  id: string,
  name?: string,
  description?: string,
  inventory?: string,
  source?: string,
  created_at?: string,
  modified_at?: string
}

const buildInventoryTabs = (inventoryId: string, intl: AnyObject) : TabItemType[] => ( [
    {
      eventKey: 0,
      title: (
        <div>
          <CaretLeftIcon/>
          {intl.formatMessage(sharedMessages.backToInventories)}
        </div>
      ),
      name: `/inventories`
    },
    { eventKey: 1,
      title: 'Details',
      name: `/inventories/inventory/${inventoryId}/details` }
  ]);

export const renderInventoryTabs = (inventoryId: string, intl) => {
  const inventory_tabs = buildInventoryTabs(inventoryId, intl);
  return <AppTabs tabItems={inventory_tabs}/>
};

const endpoint_inventory = 'http://' + getServer() + '/api/inventories/';

export const getTabFromPath = (tabs:TabItemType[], path:string ):string | undefined => {
  const currentTab=tabs.find((tabItem) => tabItem.name.split('/').pop() === path.split('/').pop());
  return currentTab?.title.toString();
};

const Inventory: React.FunctionComponent = () => {
  const [inventory, setInventory] = useState<InventoryType|undefined>(undefined);
  const { id } = useParams<{id: string}>();
  const intl = useIntl();

  useEffect(() => {
    fetch(`${endpoint_inventory}${id}`, {
      headers: {
        'Content-Type': 'application/json',
      },
    }).then(response => response.json())
      .then(data => setInventory(data));
  }, []);

  const location = useLocation();
  const currentTab = inventory?.id ?
    getTabFromPath(buildInventoryTabs(inventory.id,intl), location.pathname) :
    intl.formatMessage(sharedMessages.details);
  return (
    <React.Fragment>
      <TopToolbar breadcrumbs={[
        {
          title: intl.formatMessage(sharedMessages.inventories),
          key: 'inventories',
          to: '/inventories'
        },
        {
          title: inventory?.name,
          key: 'details',
          to: `/inventories/inventory/${inventory?.id}/details`
        },
        {
          title: currentTab || intl.formatMessage(sharedMessages.details),
          key: 'current_tab'
        }
      ]
      }>
        <Title headingLevel={"h2"}>{`${inventory?.name}`}</Title>
      </TopToolbar>
      { inventory &&
        <Switch>
          <Route path="/inventories/inventory/:id">
            <InventoryDetails
              inventory={inventory}
            />
          </Route>
        </Switch>
      }
    </React.Fragment>
  );
}

export { Inventory };
