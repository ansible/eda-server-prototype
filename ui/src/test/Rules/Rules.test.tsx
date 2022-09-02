import * as React from 'react';
import {mount} from 'enzyme';
import {Rules} from "@app/Rules/Rules";
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

describe('Rules', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should render the Rules component', async () => {
    fetchMock.mockResponse(JSON.stringify([{ id: '1', name: 'Rule 1'},
      { id: '2', name: 'Rule 2'},
      { id: '3', name: 'Rule 3'} ])
    )

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/rules']}>
          <Route path='/rules'>
            <Rules/>
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
