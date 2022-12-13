import * as React from 'react';
import { mount } from 'enzyme';
import { AppLayout } from '@app/AppLayout/AppLayout';
import { MemoryRouter } from 'react-router';
import { act } from 'react-dom/test-utils';
import { IntlProvider } from 'react-intl';
import { Route } from 'react-router-dom';
import { mockApi } from '../__mocks__/baseApi';
import { Dashboard } from '@app/Dashboard/Dashboard';
import { NotificationsPortal } from '@redhat-cloud-services/frontend-components-notifications';
import store from '../../store';
import { Provider } from 'react-redux';
import {NavExpandable, NavItem} from "@patternfly/react-core";

const ComponentWrapper = ({ children, initialEntries = ['/dashboard'] }) => (
  <Provider store={store()}>
    <IntlProvider locale="en">
      <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
        {children}
      </MemoryRouter>
      <NotificationsPortal />
    </IntlProvider>
  </Provider>
);

describe('AppLayout', () => {
  beforeAll(() => {
    mockApi.reset();
  });

  it('should render the AppLayout component', async () => {
    mockApi
      .onGet(`/api/users/me`)
      .replyOnce(200, { email: 'test@test.com', id: '1', is_active: true, is_superuser: false, is_verified: false });

    mockApi
      .onGet(`/api/audit/rules_fired`)
      .replyOnce(200, [
      {
        rule: {
          id: 1,
          name: 'Say Hello',
        },
        type: 'Playbook',
        job: {
          id: 1,
          name: 'debug',
        },
        ruleset: {
          id: 2,
          name: 'Hello Events',
        },
        status: 'successful',
        fired_date: '2022-11-17T14:54:37.813339+00:00',
      }]);

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/AppLayout']}>
          <Route path="/AppLayout">
            <AppLayout>
              <Dashboard />
            </AppLayout>
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find(NavExpandable).length).toEqual(1);
    expect(wrapper.find(NavExpandable).at(0).props().title).toEqual('Management');
    expect(wrapper.find(NavItem).length).toEqual(11);
  });
});
