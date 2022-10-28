import * as React from 'react';
import { act } from 'react-dom/test-utils';
import App from '@app/index';
import { mount } from 'enzyme';
import { Button } from '@patternfly/react-core';
import { MemoryRouter } from 'react-router';
import { AppLayout } from '@app/AppLayout/AppLayout';
import { AppRoutes } from '@app/routes';
import store from '../store';
import { Provider } from 'react-redux';
import { mockApi } from './__mocks__/baseApi';

const ComponentWrapper = ({ children }) => (
  <Provider store={store()}>
    <MemoryRouter initialEntries={['/eda/dashboard']}>{children}</MemoryRouter>
  </Provider>
);

describe('App tests', () => {
  beforeAll(() => {
    mockApi.reset();
  });

  it('should render a nav-toggle button', () => {
    const wrapper = mount(<App />);
    const button = wrapper.find(Button);
    expect(button.exists()).toBe(true);
  });

  it('should hide the sidebar on smaller viewports', async () => {
    mockApi.onGet(`/api/users/me`).replyOnce(200, { email: 'test@test.com' });
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
    await act(async () => {
      wrapper.update();
    });
    window.dispatchEvent(new Event('resize'));
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find('#page-sidebar').hasClass('pf-m-collapsed')).toBeTruthy();
  });

  it('should hide the sidebar when clicking the nav-toggle button', () => {
    mockApi.onGet(`/api/users/me`).replyOnce(200, { email: 'test@test.com' });
    Object.defineProperty(window, 'innerWidth', { writable: true, configurable: true, value: 1200 });
    const wrapper = mount(
      <ComponentWrapper>
        <AppLayout>
          <AppRoutes />
        </AppLayout>
      </ComponentWrapper>
    );
    window.dispatchEvent(new Event('resize'));
    const button = wrapper.find('#nav-toggle').hostNodes();
    button.simulate('click');
    expect(wrapper.find('#page-sidebar').hasClass('pf-m-collapsed')).toBeTruthy();
    button.simulate('click');
    expect(wrapper.find('#page-sidebar').hasClass('pf-m-collapsed')).toBeFalsy;
  });
});
