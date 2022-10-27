import * as React from 'react';
import {mount} from 'enzyme';
import {MemoryRouter} from "react-router";
import fetchMock from "jest-fetch-mock";
import {act} from "react-dom/test-utils";
import {IntlProvider} from "react-intl";
import {Modal} from "@patternfly/react-core";
import {RemoveActivation} from "@app/RemoveActivation/RemoveActivation";
import {defaultSettings} from "@app/shared/pagination";
import store from "../../store";
import {Provider} from "react-redux";
import {Route} from "react-router-dom";

const ComponentWrapper = ({ children, initialEntries=['/dashboard']}) => (
  <Provider store={store()}>
    <IntlProvider locale="en">
      <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
        {children}
      </MemoryRouter>
    </IntlProvider>
  </Provider>
);

describe('RemoveActivation', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should render the Remove Activation modal', async () => {
    fetchMock.mockResponse(JSON.stringify({
          name: 'Activation 1',
          id: 1
       })
    )
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/activations/remove/1']}>
          <Route path='/activations/remove/:id'>
            <RemoveActivation fetchData={()=>[]} pagination={defaultSettings} resetSelectedActivations={()=>[]}/>
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });

    expect(wrapper.find(Modal).at(0).props().title).toEqual("Delete rulebook activation");
    expect(wrapper.find('Text').at(0).props().children).toEqual('Are you sure you want to delete the rulebook activation below?');
    expect(wrapper.find('Text').at(1).props().children.props.children.at(1)).toEqual('Activation 1');
  });

 it('should render the bulk Remove Rulebook Activations modal', async () => {
    fetchMock.mockResponse(JSON.stringify({
        name: 'Activation 1',
        id: 1
      })
    )
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/activations/remove/1']}>
          <RemoveActivation ids={[1,2,3,4]} fetchData={()=>[]} pagination={defaultSettings} resetSelectedActivations={()=>[]}/>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });

    expect(wrapper.find(Modal).at(0).props().title).toEqual("Delete selected rulebook activations");
    expect(wrapper.find('Text').at(0).props().children).toEqual('Are you sure you want to delete the selected rulebook activations?');
    expect(wrapper.find('Text').at(1).props().children.props.children.at(1)).toEqual('4 selected');
  });
})
