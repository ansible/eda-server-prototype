import * as React from 'react';
import { mount } from 'enzyme';
import { ActionsHosts } from '@app/Actions/actions-hosts';
import { MemoryRouter } from 'react-router';
import { act } from 'react-dom/test-utils';
import { IntlProvider } from 'react-intl';
import { Route } from 'react-router-dom';
import { mockApi } from '../__mocks__/baseApi';
import {ActionsRules} from "@app/Actions/actions-rules";

const ComponentWrapper = ({ children, initialEntries = ['/dashboard'] }) => (
  <IntlProvider locale="en">
    <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
      {children}
    </MemoryRouter>
  </IntlProvider>
);

describe('ActionsHosts', () => {
  beforeAll(() => {
    mockApi.reset();
  });

  it('should render the ActionsView component', async () => {
    mockApi.onGet(`/api/actions/rules_fired`).replyOnce(200, [
      { id: '1', name: 'Rule 1' },
      { id: '2', name: 'Rule 2' },
      { id: '3', name: 'Rule3 3' },
    ]);

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/actions']}>
          <Route path="/actions/rules">
            <ActionsRules />
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
