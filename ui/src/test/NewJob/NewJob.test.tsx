import * as React from 'react';
import { mount } from 'enzyme';
import { MemoryRouter } from 'react-router';
import { act } from 'react-dom/test-utils';
import { IntlProvider } from 'react-intl';
import { Route } from 'react-router-dom';
import { Button } from '@patternfly/react-core';
import store from '../../store';
import { Provider } from 'react-redux';
import { NewJob } from '@app/NewJob/NewJob';
import { mockApi } from '../__mocks__/baseApi';

const ComponentWrapper = ({ children, initialEntries = ['/dashboard'] }) => (
  <Provider store={store()}>
    <IntlProvider locale="en">
      <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
        {children}
      </MemoryRouter>
    </IntlProvider>
  </Provider>
);

describe('NewJob', () => {
  beforeAll(() => {
    mockApi.reset();
  });

  it('should render the New Job form', async () => {
    mockApi.onGet(`/api/extra_vars`).replyOnce(200, [
      { id: '1', name: 'Var 1' },
      { id: '2', name: 'Var 2' },
    ]);
    mockApi.onGet(`/api/inventories`).replyOnce(200, [
      { id: '1', name: 'Inventory 1' },
      { id: '2', name: 'Inventory 2' },
    ]);
    mockApi.onGet(`/api/playbooks`).replyOnce(200, [
      { id: '1', name: 'Playbook 1' },
      { id: '2', name: 'Playbook 2' },
      { id: '3', name: 'Playbook 3' },
    ]);

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/new-job']}>
          <Route path="/new-job">
            <NewJob />
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find(Button).length).toEqual(2);
    wrapper.find(Button).at(0).simulate('click');
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find('div').at(6).at(0).props().children.at(1)).toEqual('Select a playbook');
  });
});
