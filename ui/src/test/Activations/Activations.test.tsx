import * as React from 'react';
import {mount} from 'enzyme';
import {Activations} from "@app/Activations/Activations";
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

describe('Activations', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should render the Activations component', async () => {
    fetchMock.mockResponse(JSON.stringify([{ id: '1', name: 'Activation 1'},
      { id: '2', name: 'Activation 2'},
      { id: '3', name: 'Activation 3'} ])
    )

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/activations']}>
          <Route path='/activations'>
            <Activations/>
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
