import * as React from 'react';
import {mount} from 'enzyme';
import {Activation} from "@app/Activation/Activation";
import {MemoryRouter} from "react-router";
import fetchMock from "jest-fetch-mock";
import {act} from "react-dom/test-utils";
import {IntlProvider} from "react-intl";
import {Route} from "react-router-dom";
import {Tab, TextInput, Title} from "@patternfly/react-core";
import {ActivationDetails} from "@app/Activation/activation-details";

const ComponentWrapper = ({ children, initialEntries=['/dashboard']}) => (
  <IntlProvider locale="en">
    <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
      {children}
    </MemoryRouter>
  </IntlProvider>
);

describe('Activation', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should render the Activation component tabs', async () => {
    fetchMock.mockResponse(JSON.stringify({
          name: 'Activation 1',
          id: 1,
          ruleset_id: '2',
          ruleset_name: 'Ruleset 1',
          inventory_id: '3',
          inventory_name: 'Inventory 1'
      })
    )
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/activation/1']}>
          <Route path='/activation/:id'>
            <Activation/>
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find(Tab).length).toEqual(4);
    expect(wrapper.find(Tab).at(0).props().title.props.children[1]).toEqual("Back to Rulebook Activations");
    expect(wrapper.find(Tab).at(1).props().title).toEqual('Details');
    expect(wrapper.find(Tab).at(2).props().title).toEqual('Jobs');
  });

  it('should render the Activation details with EDA container image', async () => {
    fetchMock.mockResponse(JSON.stringify({
        name: 'Activation 1',
        id: 1,
        ruleset_id: '2',
        ruleset_name: 'Ruleset 1',
        inventory_id: '3',
        inventory_name: 'Inventory 1'
      })
    )
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/activation/1']}>
          <Route path='/activation/:id'>
            <ActivationDetails activation={{
              id: '1',
              name: 'Activation 1',
              description: '',
              ruleset_id: '2',
              ruleset_name: 'Ruleset 1',
              inventory_id: '3',
              inventory_name: 'Inventory 1'}}/>
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find(Title).length).toEqual(13);
    expect(wrapper.find(Title).at(1).props().children).toEqual('EDA container image');
  });
});
