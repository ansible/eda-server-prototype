import * as React from 'react';
import { mount, render, shallow } from 'enzyme';
import { MemoryRouter } from 'react-router';
import { act } from 'react-dom/test-utils';
import { IntlProvider } from 'react-intl';
import { Route } from 'react-router-dom';
import { Button, TextInput } from '@patternfly/react-core';
import store from '../../store';
import { Provider } from 'react-redux';
import { NewInventory } from '@app/NewInventory/NewInventory';
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

describe('NewInventory', () => {
  beforeAll(() => {
    mockApi.reset();
    window.HTMLCanvasElement.prototype.getContext = () => ({} as any);
  });

  it('should render the NewInventory form', async () => {
    mockApi.onPost(`/api/inventories`).replyOnce(200, {
      name: 'Inventory 1',
      id: 1,
      inventory: 'inventory',
    });

    let wrapper;
    await act(async () => {
      wrapper = render(
        <ComponentWrapper initialEntries={['/new-inventory']}>
          <Route path="/new-inventory">
            <NewInventory />
          </Route>
        </ComponentWrapper>
      );
    });

    expect(wrapper).toMatchSnapshot();
  });
});
