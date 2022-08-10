import * as React from 'react';
import { act } from 'react-dom/test-utils';
import App from '@app/index';
import { mount, shallow } from 'enzyme';
import { Button } from '@patternfly/react-core';
import {MemoryRouter} from "react-router";
import {AppLayout} from "@app/AppLayout/AppLayout";
import {AppRoutes} from "@app/routes";

const ComponentWrapper = ({ children }) => (
    <MemoryRouter>{children}</MemoryRouter>
);

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
    Object.defineProperty(window, 'innerWidth', { writable: true, configurable: true, value: 200 });
    let wrapper;
    await act(async () => {
        wrapper = mount(
        <ComponentWrapper>
          <AppLayout>
            <AppRoutes />
          </AppLayout>
        </ComponentWrapper>
      );
    });
    window.dispatchEvent(new Event('resize'));
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find('sidebar').hasClass('pf-m-collapsed')).toBeTruthy();
  });

  it('should expand the sidebar on larger viewports', () => {
    Object.defineProperty(window, 'innerWidth', { writable: true, configurable: true, value: 1200 });
    const wrapper = mount(<App />);
    window.dispatchEvent(new Event('resize'));
    expect(wrapper.find('#page-sidebar').hasClass('pf-m-expanded')).toBeTruthy();
  });

  it('should hide the sidebar when clicking the nav-toggle button', () => {
    Object.defineProperty(window, 'innerWidth', { writable: true, configurable: true, value: 1200 });
    const wrapper = mount(<App />);
    window.dispatchEvent(new Event('resize'));
    const button = wrapper.find('#nav-toggle').hostNodes();
    expect(wrapper.find('#page-sidebar').hasClass('pf-m-expanded')).toBeTruthy();
    button.simulate('click');
    expect(wrapper.find('#page-sidebar').hasClass('pf-m-collapsed')).toBeTruthy();
    expect(wrapper.find('#page-sidebar').hasClass('pf-m-expanded')).toBeFalsy();
  });
});
