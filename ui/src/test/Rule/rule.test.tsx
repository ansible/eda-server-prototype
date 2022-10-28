import * as React from 'react';
import { mount } from 'enzyme';
import { Rule } from '@app/Rule/Rule';
import { MemoryRouter } from 'react-router';
import { act } from 'react-dom/test-utils';
import { IntlProvider } from 'react-intl';
import { Route } from 'react-router-dom';
import { Tab } from '@patternfly/react-core';
import { mockApi } from '../__mocks__/baseApi';

const ComponentWrapper = ({ children, initialEntries = ['/dashboard'] }) => (
  <IntlProvider locale="en">
    <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
      {children}
    </MemoryRouter>
  </IntlProvider>
);

describe('RuleSet', () => {
  beforeAll(() => {
    mockApi.reset();
  });

  it('should render the RuleSet component tabs', async () => {
    mockApi.onGet(`/api/rules/1`).replyOnce(200, {
      name: 'Ruleset 1',
      id: '1',
    });
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/rule/1']}>
          <Route path="/rule/:id">
            <Rule />
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find(Tab).length).toEqual(2);
    expect(wrapper.find(Tab).at(0).props().title.props.children).toContain('Back to Rules');
    expect(wrapper.find(Tab).at(1).props().title).toEqual('Details');
  });
});
