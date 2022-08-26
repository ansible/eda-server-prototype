import * as React from 'react';
import {mount, shallow} from 'enzyme';
import {RuleSets} from "@app/RuleSetFiles/RuleSetFiles";
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

describe('RuleSets', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should render the RuleSets component', async () => {
    fetchMock.mockResponse(JSON.stringify([{ id: '1', name: 'RuleSet 1'},
      { id: '2', name: 'RuleSet 2'},
      { id: '3', name: 'RuleSet 3'} ])
    )

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/rulesets']}>
          <Route path='/rulesets'>
            <RuleSets/>
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
