import * as React from 'react';
import { mount } from 'enzyme';
import { AuditHosts } from '@app/AuditView/audit-hosts';
import { MemoryRouter } from 'react-router';
import { act } from 'react-dom/test-utils';
import { IntlProvider } from 'react-intl';
import { Route } from 'react-router-dom';
import { mockApi } from '../__mocks__/baseApi';

const ComponentWrapper = ({ children, initialEntries = ['/dashboard'] }) => (
  <IntlProvider locale="en">
    <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
      {children}
    </MemoryRouter>
  </IntlProvider>
);

describe('AuditHosts', () => {
  beforeAll(() => {
    mockApi.reset();
  });

  it('should render the AuditView component', async () => {
    mockApi.onGet(`/api/audit/hosts_changed`).replyOnce(200, [
      { id: '1', name: 'Host 1' },
      { id: '2', name: 'Host 2' },
      { id: '3', name: 'Host 3' },
    ]);

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/audit']}>
          <Route path="/audit/rules">
            <AuditHosts />
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper).toMatchSnapshot();
  });
});
