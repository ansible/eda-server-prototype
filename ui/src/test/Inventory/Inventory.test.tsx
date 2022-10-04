import * as React from 'react';
import {mount} from 'enzyme';
import {Inventory} from "@app/Inventory/inventory";
import {MemoryRouter} from "react-router";
import fetchMock from "jest-fetch-mock";
import {act} from "react-dom/test-utils";
import {IntlProvider} from "react-intl";
import {Route} from "react-router-dom";
import {Tab} from "@patternfly/react-core";

const ComponentWrapper = ({ children, initialEntries=['/dashboard']}) => (
  <IntlProvider locale="en">
    <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
      {children}
    </MemoryRouter>
  </IntlProvider>
);

describe('Inventory', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should render the Inventory component tabs', async () => {
    fetchMock.mockResponse(JSON.stringify({
          name: 'Inventory 1',
          id: 1,
          inventory: 'inventory content'
      })
    )
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/inventories/inventory/1']}>
          <Route path='/inventories/inventory/:id'>
            <Inventory/>
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find(Tab).length).toEqual(2);
    expect(wrapper.find(Tab).at(0).props().title.props.children[1]).toEqual("Back to Inventories");
    expect(wrapper.find(Tab).at(1).props().title).toEqual('Details');
  });
});
