import * as React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  Nav,
  NavList,
  NavItem,
  NavExpandable,
  Page,
  PageHeader,
  PageSidebar,
  SkipToContent,
  PageHeaderTools,
  DropdownItem
} from '@patternfly/react-core';
import { routes, IAppRoute, IAppRouteGroup } from '@app/routes';
import {ExternalLinkAltIcon, QuestionCircleIcon } from '@patternfly/react-icons';
import { useState } from 'react';
import { AboutModalWindow } from './about-modal';
import Logo from '../../assets/images/logo-large.svg';
import { SmallLogo } from './small-logo';
import { APPLICATION_TITLE } from '../utils/constants.ts';
import { StatefulDropdown } from './stateful-dropdown';

interface IAppLayout {
  children: React.ReactNode;
}

const AppLayout: React.FunctionComponent<IAppLayout> = ({ children }) => {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [isNavOpen, setIsNavOpen] = useState(true);
  const [isMobileView, setIsMobileView] = useState(true);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [isNavOpenMobile, setIsNavOpenMobile] = useState(false);
  const [aboutModalVisible, setAboutModalVisible] = useState(false);

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const onPageResize = (props: { mobileView: boolean; windowSize: number }) => {
    setIsMobileView(props.mobileView);
  };

  const aboutModal = () => {
    return (
      <AboutModalWindow
        isOpen={aboutModalVisible}
        trademark=""
        brandImageSrc={Logo}
        onClose={() => setAboutModalVisible(false)}
        brandImageAlt={`Application Logo`}
        productName={APPLICATION_TITLE}
      />
    );
  };

  const docsDropdownItems = [
    <DropdownItem
      key="customer_support"
      href="https://access.redhat.com/support"
      target="_blank"
    >
      Customer Support <ExternalLinkAltIcon />
    </DropdownItem>,
    <DropdownItem
      key="training"
      href="https://www.ansible.com/resources/webinars-training"
      target="_blank"
    >
      Training <ExternalLinkAltIcon />
    </DropdownItem>,
    <DropdownItem key="about" onClick={() => setAboutModalVisible(true)}>
      {`About`}
    </DropdownItem>
  ];

  const headerNav = () => (
    <PageHeader
      logo={<SmallLogo alt={APPLICATION_TITLE} />}
      headerTools={
        <PageHeaderTools>
          <div>
            <StatefulDropdown
              ariaLabel={'docs-dropdown'}
              defaultText={<QuestionCircleIcon />}
              items={docsDropdownItems}
              toggleType="icon"
            />
          </div>
        </PageHeaderTools>
      }
      showNavToggle
    />
  );

  const location = useLocation();

  const renderNavItem = (route: IAppRoute, index: number) => (
    <NavItem key={`${route.label}-${index}`} id={`${route.label}-${index}`} isActive={route.path === location.pathname}>
      <NavLink exact={route.exact} to={route.path}>
        {route.label}
      </NavLink>
    </NavItem>
  );

  const renderNavGroup = (group: IAppRouteGroup, groupIndex: number) => (
    <NavExpandable
      key={`${group.label}-${groupIndex}`}
      id={`${group.label}-${groupIndex}`}
      title={group.label}
      isActive={group.routes.some((route) => route.path === location.pathname)}
    >
      {group.routes.map((route, idx) => route.label && renderNavItem(route, idx))}
    </NavExpandable>
  );

  const Navigation = (
    <Nav id="nav-primary-simple" theme="dark">
      <NavList id="nav-list-simple">
        {routes.map(
          (route, idx) => route.label && (!route.routes ? renderNavItem(route, idx) : renderNavGroup(route, idx))
        )}
      </NavList>
    </Nav>
  );

  const Sidebar = (
    <PageSidebar
      theme="dark"
      nav={Navigation}
      isNavOpen={isMobileView ? isNavOpenMobile : isNavOpen} />
  );

  const pageId = 'primary-app-container';

  const PageSkipToContent = (
    <SkipToContent onClick={(event) => {
      event.preventDefault();
      const primaryContentContainer = document.getElementById(pageId);
      primaryContentContainer && primaryContentContainer.focus();
    }} href={`#${pageId}`}>
      Skip to Content
    </SkipToContent>
  );
  return (
    <Page
      mainContainerId={pageId}
      header={headerNav()}
      sidebar={Sidebar}
      onPageResize={onPageResize}
      skipToContent={PageSkipToContent}>
      {aboutModalVisible && aboutModal()}
      {children}
    </Page>
  );
};

export { AppLayout };
