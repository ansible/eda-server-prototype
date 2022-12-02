import * as React from 'react';
import { mount } from 'enzyme';
import { AuditHosts } from '@app/AuditView/audit-hosts';
import { MemoryRouter } from 'react-router';
import { act } from 'react-dom/test-utils';
import { IntlProvider } from 'react-intl';
import { Route } from 'react-router-dom';
import { mockApi } from '../__mocks__/baseApi';
import {AuditRules} from "@app/AuditView/audit-rules";

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
    mockApi.onGet(`/api/audit/rules_fired`).replyOnce(200, [
      { id: '1', name: 'Rule 1' },
      { id: '2', name: 'Rule 2' },
      { id: '3', name: 'Rule3 3' },
    ]);

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/audit']}>
          <Route path="/audit/rules">
            <AuditRules />
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
