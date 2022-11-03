import * as React from 'react';
import { mount } from 'enzyme';
import { MemoryRouter } from 'react-router';
import fetchMock from 'jest-fetch-mock';
import { act } from 'react-dom/test-utils';
import { IntlProvider } from 'react-intl';
import { Modal } from '@patternfly/react-core';
import { RemoveInventory } from '@app/RemoveInventory/RemoveInventory';
import { defaultSettings } from '@app/shared/pagination';
import store from '../../store';
import { Provider } from 'react-redux';
import { Route } from 'react-router-dom';

const ComponentWrapper = ({ children, initialEntries = ['/dashboard'] }) => (
  <Provider store={store()}>
    <IntlProvider locale="en">
      <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
        {children}
      </MemoryRouter>
    </IntlProvider>
  </Provider>
);

describe('RemoveInventory', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should render the Remove Inventory modal', async () => {
    fetchMock.mockResponse(
      JSON.stringify({
        name: 'Inventory 1',
        id: 1,
      })
    );
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/inventories/remove/1']}>
          <Route path="/inventories/remove/:id">
            <RemoveInventory fetchData={() => []} pagination={defaultSettings} resetSelectedInventories={() => []} />
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });

    expect(wrapper.find(Modal).at(0).props().title).toEqual('Delete inventory');
    expect(wrapper.find('Text').at(0).props().children).toEqual('Are you sure you want to delete the inventory below?');
    expect(wrapper.find('Text').at(1).props().children.props.children.at(1)).toEqual('Inventory 1');
  });

  it('should render the bulk Remove Inventories modal', async () => {
    fetchMock.mockResponse(
      JSON.stringify({
        name: 'Inventory 1',
        id: 1,
      })
    );
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/inventories/remove/1']}>
          <RemoveInventory
            ids={[1, 2, 3, 4, 5]}
            fetchData={() => []}
            pagination={defaultSettings}
            resetSelectedInventories={() => []}
          />
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });

    expect(wrapper.find(Modal).at(0).props().title).toEqual('Delete inventories');
    expect(wrapper.find('Text').at(0).props().children).toEqual(
      'Are you sure you want to delete the selected inventories?'
    );
    expect(wrapper.find('Text').at(1).props().children.props.children.at(1)).toEqual('5 selected');
  });
});
