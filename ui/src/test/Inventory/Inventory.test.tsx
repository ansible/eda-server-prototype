import * as React from 'react';
import { mount } from 'enzyme';
import { Inventory } from '@app/Inventory/inventory';
import { MemoryRouter } from 'react-router';
import { act } from 'react-dom/test-utils';
import { IntlProvider } from 'react-intl';
import { Route } from 'react-router-dom';
import { DropdownItem, KebabToggle, Tab } from '@patternfly/react-core';
import { mockApi } from '../__mocks__/baseApi';

const ComponentWrapper = ({ children, initialEntries = ['/dashboard'] }) => (
  <IntlProvider locale="en">
    <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
      {children}
    </MemoryRouter>
  </IntlProvider>
);

describe('Inventory', () => {
  beforeAll(() => {
    mockApi.reset();
  });

  it('should render the Inventory component tabs', async () => {
    mockApi.onGet(`/api/inventory/1`).replyOnce(200, {
      name: 'Inventory 1',
      id: 1,
      inventory: 'inventory content',
    });
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/inventories/inventory/1']}>
          <Route path="/inventories/inventory/:id">
            <Inventory />
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find(Tab).length).toEqual(2);
    expect(wrapper.find(Tab).at(0).props().title.props.children[1]).toEqual('Back to Inventories');
    expect(wrapper.find(Tab).at(1).props().title).toEqual('Details');
  });

  it('has a top toolbar kebab menu', async () => {
    mockApi.onGet(`/api/inventory/1`).replyOnce(200, {
      name: 'Inventory 1',
      id: 1,
      inventory: 'inventory content',
    });
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/inventories/inventory/1']}>
          <Route path="/inventories/inventory/:id">
            <Inventory />
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find(KebabToggle).length).toEqual(1);
    expect(wrapper.find('.pf-c-dropdown__toggle').length).toEqual(1);
    wrapper.find('.pf-c-dropdown__toggle').simulate('click');
    wrapper.update();
    expect(wrapper.find(DropdownItem).length).toEqual(2);
    expect(wrapper.find(DropdownItem).at(0).props().component.props.children).toEqual('Edit');
    expect(wrapper.find(DropdownItem).at(1).props().component.props.children).toEqual('Delete');
  });
});
