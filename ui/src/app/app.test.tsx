import * as React from 'react';
import { act } from 'react-dom/test-utils';
import App from '@app/index';
import { mount, shallow } from 'enzyme';
import { Button } from '@patternfly/react-core';
import {MemoryRouter} from "react-router";
import fetchMock from "jest-fetch-mock";
import {AppLayout} from "@app/AppLayout/AppLayout";
import {AppRoutes} from "@app/routes";

const ComponentWrapper = ({ children }) => (
    <MemoryRouter initialEntries={['/eda/dashboard']}>{children}</MemoryRouter>
);
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useLocation: () => ({
    pathname: "/eda/dashboard"
  })
}));

describe('App tests', () => {
  test('should render default App component', () => {
    const view = shallow(<App />);
    expect(view).toMatchSnapshot();
  });

  it('should render a nav-toggle button', () => {
    const wrapper = mount(<App />);
    const button = wrapper.find(Button);
    expect(button.exists()).toBe(true);
  });

  it('should hide the sidebar on smaller viewports', async () => {
    fetchMock.mockResponse(JSON.stringify({}))
    Object.defineProperty(window, 'innerWidth', { writable: true, configurable: true, value: 200 });
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper>
          <AppLayout>
            <AppRoutes/>
          </AppLayout>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });
    window.dispatchEvent(new Event('resize'));
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find('#page-sidebar').hasClass('pf-m-collapsed')).toBeTruthy();
  });

  it('should expand the sidebar on larger viewports', async () => {
    fetchMock.mockResponse(JSON.stringify({}))
    Object.defineProperty(window, 'innerWidth', { writable: true, configurable: true, value: 1200 });
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper>
          <AppLayout>
            <AppRoutes/>
          </AppLayout>
        </ComponentWrapper>
      );
    });
    window.dispatchEvent(new Event('resize'));
    expect(wrapper.find('#page-sidebar').hasClass('pf-m-expanded')).toBeTruthy();
  });

  it('should hide the sidebar when clicking the nav-toggle button', () => {
    Object.defineProperty(window, 'innerWidth', { writable: true, configurable: true, value: 1200 });
    const wrapper = mount(
      <ComponentWrapper>
        <AppLayout>
          <AppRoutes/>
        </AppLayout>
      </ComponentWrapper>);
    window.dispatchEvent(new Event('resize'));
    const button = wrapper.find('#nav-toggle').hostNodes();
    //expect(wrapper.find('#page-sidebar').hasClass('pf-m-expanded')).toBeTruthy();
    button.simulate('click');
    expect(wrapper.find('#page-sidebar').hasClass('pf-m-collapsed')).toBeTruthy();
    expect(wrapper.find('#page-sidebar').hasClass('pf-m-expanded')).toBeFalsy();
  });
});
