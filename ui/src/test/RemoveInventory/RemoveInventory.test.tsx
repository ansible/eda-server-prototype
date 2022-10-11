import * as React from 'react';
import {mount} from 'enzyme';
import {MemoryRouter} from "react-router";
import fetchMock from "jest-fetch-mock";
import {act} from "react-dom/test-utils";
import {IntlProvider} from "react-intl";
import {Modal} from "@patternfly/react-core";
import {RemoveInventory} from "@app/RemoveInventory/RemoveInventory";
import {defaultSettings} from "@app/shared/pagination";
import store from "../../store";
import {Provider} from "react-redux";

const ComponentWrapper = ({ children, initialEntries=['/dashboard']}) => (
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
    fetchMock.mockResponse(JSON.stringify({
          name: 'Inventory 1',
          id: 1
       })
    )
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/inventories/remove/1']}>
            <RemoveInventory fetchData={()=>[]} pagination={defaultSettings} setSelectedInventories={()=>[]}/>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });

    expect(wrapper.find(Modal).at(0).props().title).toEqual("Delete inventory");
    expect(wrapper.find('Text').at(0).props().children).toEqual('Are you sure you want to delete the inventory below?');
    expect(wrapper.find('Text').at(1).props().children.props.children).toEqual('Inventory 1');
  });
})
