import * as React from 'react';
import {mount} from 'enzyme';
import {MemoryRouter} from "react-router";
import fetchMock from "jest-fetch-mock";
import {act} from "react-dom/test-utils";
import {IntlProvider} from "react-intl";
import {Modal} from "@patternfly/react-core";
import {RemoveActivation} from "@app/RemoveActivation/RemoveActivation";
import {defaultSettings} from "@app/shared/pagination";

const ComponentWrapper = ({ children, initialEntries=['/dashboard']}) => (
  <IntlProvider locale="en">
    <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
      {children}
    </MemoryRouter>
  </IntlProvider>
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
            <RemoveActivation fetchData={()=>[]} pagination={defaultSettings} setSelectedActivations={()=>[]}/>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });

    expect(wrapper.find(Modal).at(0).props().title).toEqual("Delete rulebook activation");
    expect(wrapper.find('Text').at(0).props().children).toEqual('Are you sure you want to delete the rulebook activation below?');
    expect(wrapper.find('Text').at(1).props().children.props.children).toEqual('Activation 1');
  });
})
