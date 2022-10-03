import * as React from 'react';
import {mount, shallow} from 'enzyme';
import {RuleSet} from "@app/RuleSet/ruleset";
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

describe('RuleSet', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should render the RuleSet component tabs', async () => {
    fetchMock.mockResponse(JSON.stringify({
          name: 'RuleSet 1',
          id: 1,
       })
    )
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/ruleset/1']}>
          <Route path='/ruleset/:id'>
            <RuleSet/>
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });
    //expect(wrapper).toMatchSnapshot();
    expect(wrapper.find(Tab).length).toEqual(4);
    expect(wrapper.find(Tab).at(0).props().title.props.children).toContain('Back to Rule Sets');
    expect(wrapper.find(Tab).at(1).props().title).toEqual('Details');
    expect(wrapper.find(Tab).at(2).props().title).toEqual('Rules');
    expect(wrapper.find(Tab).at(3).props().title).toEqual('Sources');
  });
});
