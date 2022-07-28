import * as React from 'react';
import {NavLink, useLocation} from 'react-router-dom';
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
  DropdownItem,
  NavGroup
} from '@patternfly/react-core';
import { routes, IAppRoute, IAppRouteGroup } from '@app/routes';
import {ExternalLinkAltIcon, QuestionCircleIcon } from '@patternfly/react-icons';
import {useEffect, useState} from 'react';
import Logo from '../../assets/images/logo-large.svg';
import { SmallLogo } from './small-logo';
import { APPLICATION_TITLE } from '../utils/constants';
import { StatefulDropdown } from './stateful-dropdown';
import {getUser, logoutUser} from '@app/shared/auth';
import {User} from "@app/shared/types/common-types";
import {AboutModalWindow} from "@app/AppLayout/about-modal";

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
  const [user, setUser] = useState<User | undefined>(undefined);

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const onPageResize = (props: { mobileView: boolean; windowSize: number }) => {
    setIsMobileView(props.mobileView);
  };

  const aboutModal = () => {
    return (
      <AboutModalWindow
        isOpen={aboutModalVisible}
        user={user}
        trademark=""
        brandImageSrc={Logo}
        onClose={() => setAboutModalVisible(false)}
        brandImageAlt={`Application Logo`}
        productName={APPLICATION_TITLE}
      />
    );
  };

  let userName = '';
  const location = useLocation();
  const index = window.location.href.indexOf(window.location.pathname);
  const baseUrl = window.location.href.substr(0, index);

  useEffect(() => {
    getUser()
      .then(response => response.json())
      .then(data => setUser(data || undefined));
  }, []);

  if (user) {
    if (user.first_name || user.last_name) {
      userName = user.first_name + ' ' + user.last_name;
    } else {
      userName = user.email;
    }
  }

  const userDropdownItems = [
      <DropdownItem isDisabled key="username">
        Username: {user?.email || ''}
      </DropdownItem>,
      <DropdownItem
        key="logout"
        aria-label={'logout'}
        onClick={() =>
          logoutUser().then(() => {
            setUser(undefined);
            window.location.replace(
              baseUrl
            );
          })
        }
      >
        {`Logout`}
      </DropdownItem>
    ];

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
            <StatefulDropdown
              ariaLabel={'user-dropdown'}
              defaultText={user?.email}
              items={userDropdownItems}
              toggleType="dropdown"
            />

          </div>
        </PageHeaderTools>
      }
      showNavToggle
    />
  );

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
      <NavGroup title={APPLICATION_TITLE}/>
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
