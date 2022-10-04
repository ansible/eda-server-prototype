import * as React from 'react';
import {mount} from 'enzyme';
import {Inventories} from "@app/Inventories/Inventories";
import {MemoryRouter} from "react-router";
import fetchMock from "jest-fetch-mock";
import {act} from "react-dom/test-utils";
import {IntlProvider} from "react-intl";
import {Route} from "react-router-dom";

const ComponentWrapper = ({ children, initialEntries=['/dashboard']}) => (
  <IntlProvider locale="en">
    <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
      {children}
    </MemoryRouter>
  </IntlProvider>
);

describe('Inventories', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should render the Inventories component', async () => {
    fetchMock.mockResponse(JSON.stringify([{ id: '1', name: 'Inventory 1'},
      { id: '2', name: 'Inventory 2'},
      { id: '3', name: 'Inventory 3'} ])
    )

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/inventories']}>
          <Route path='/inventories'>
            <Inventories/>
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
