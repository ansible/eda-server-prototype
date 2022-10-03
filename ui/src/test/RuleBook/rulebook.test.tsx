import * as React from 'react';
import {mount} from 'enzyme';
import {RuleBook} from "@app/RuleBook/rulebook";
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

describe('RuleBook', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should render the RuleBook component tabs', async () => {
    fetchMock.mockResponse(JSON.stringify({
          name: 'RuleBook 1',
          id: 1,
          project: {id: '1', name: 'Project 1'},
          rulesets: {id: '1', name: 'Project 1'}
      })
    )
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/rulebooks/rulebook/1']}>
          <Route path='/rulebooks/rulebook/:id'>
            <RuleBook/>
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find(Tab).length).toEqual(3);
    expect(wrapper.find(Tab).at(0).props().title.props.children).toContain('Back to Rulebooks');
    expect(wrapper.find(Tab).at(1).props().title).toEqual('Details');
    expect(wrapper.find(Tab).at(2).props().title).toEqual('Rule sets');
  });
});
