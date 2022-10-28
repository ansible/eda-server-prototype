import * as React from 'react';
import { mount } from 'enzyme';
import { MemoryRouter } from 'react-router';
import { act } from 'react-dom/test-utils';
import { IntlProvider } from 'react-intl';
import { Route } from 'react-router-dom';
import { Button } from '@patternfly/react-core';
import store from '../../store';
import { Provider } from 'react-redux';
import { NewActivation } from '@app/NewActivation/NewActivation';
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

describe('NewActivation', () => {
  beforeAll(() => {
    mockApi.reset();
  });

  it('should render the NewActivation form', async () => {
    mockApi.onGet(`/api/rulebooks`).replyOnce(200, [
      { id: '1', name: 'RuleBook 1' },
      { id: '2', name: 'RuleBook 2' },
      { id: '3', name: 'RuleBook 3' },
    ]);
    mockApi.onGet(`/api/extra_vars`).replyOnce(200, [
      { id: '1', name: 'Var 1' },
      { id: '2', name: 'Var 2' },
    ]);
    mockApi.onGet(`/api/inventories`).replyOnce(200, [
      { id: '1', name: 'Inventory 1' },
      { id: '2', name: 'Inventory 2' },
    ]);
    mockApi.onGet(`/api/projects`).replyOnce(200, [
      { id: '1', name: 'Project 1', url: 'Url1' },
      { id: '2', name: 'Project 2', url: 'Url2' },
    ]);
    mockApi.onPost(`/api/job_instance/1`).replyOnce(200, {
      name: 'Activation 1',
      id: 1,
      ruleset_id: '2',
      ruleset_name: 'Ruleset 1',
      inventory_id: '3',
      inventory_name: 'Inventory 1',
    });

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/new-activation']}>
          <Route path="/new-activation">
            <NewActivation />
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
    expect(wrapper.find('div').at(8).at(0).props().children.at(1)).toEqual('Enter a rulebook activation name');
  });
});
