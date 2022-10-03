import * as React from 'react';
import {mount} from 'enzyme';
import {RuleBooks} from "@app/RuleBooks/RuleBooks";
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

describe('RuleBooks', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should render the RuleBooks component', async () => {
    fetchMock.mockResponse(JSON.stringify([{ id: '1', name: 'RuleBook 1'},
      { id: '2', name: 'RuleBook 2'},
      { id: '3', name: 'RuleBook 3'} ])
    )

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/rulebooks']}>
          <Route path='/rulebooks'>
            <RuleBooks/>
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
