/* eslint-disable react/prop-types */
import React from 'react';
import { Tabs, Tab } from '@patternfly/react-core';
import { useHistory, useLocation } from 'react-router-dom';

export interface AppTabsProps {
  tabItems: {
    name: string;
    eventKey: number;
    title: React.ReactNode;
  }[];
  defaultActive?: number;
}
const AppTabs: React.ComponentType<AppTabsProps> = ({ tabItems, defaultActive = 1 }) => {
  const { push } = useHistory();
  const { pathname, search } = useLocation();
  const activeTab = tabItems.find(({ name }) => name.split('/').pop() === pathname.split('/').pop());
  const handleTabClick = (_event: React.MouseEvent<HTMLElement, MouseEvent>, tabIndex: number | string) =>
    push({ pathname: tabItems[tabIndex as number].name, search });

  return (
    <Tabs
      activeKey={activeTab ? activeTab.eventKey : defaultActive}
      onSelect={handleTabClick}
      style={{
        backgroundColor: 'var(--pf-global--palette--white)',
      }}
    >
      {tabItems.map((item) => (
        <Tab title={item.title} key={item.eventKey} eventKey={item.eventKey} name={item.name} />
      ))}
    </Tabs>
  );
};

export default AppTabs;
