/* eslint-disable react/prop-types */
import React from 'react';
import { Tabs, Tab } from '@patternfly/react-core';
import {useHistory, useLocation} from 'react-router-dom';

export interface AppTabsProps {
  tabItems: {
    name: string;
    eventKey: number;
    title: string;
    disabled?: boolean;
  }[];
}
const AppTabs: React.ComponentType<AppTabsProps> = ({ tabItems }) => {
  const { push } = useHistory();
  const { pathname, search } = useLocation();
  const activeTab = tabItems.find(({ name }) => pathname.includes(name));
  const handleTabClick = (
    _event: React.MouseEvent<HTMLElement, MouseEvent>,
    tabIndex: number | string
  ) => push({ pathname: tabItems[tabIndex as number].name, search });

  return (
    <Tabs
      activeKey={activeTab ? activeTab.eventKey : 0}
      onSelect={handleTabClick}
    >
      {tabItems.map((item) => (
        <Tab
          title={item.title}
          key={item.eventKey}
          eventKey={item.eventKey}
          name={item.name}
          disabled={item.disabled}
        />
      ))}
    </Tabs>
  );
};

export default AppTabs;
