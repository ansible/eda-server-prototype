import * as React from 'react';
import { mount } from 'enzyme';
import { RuleBook } from '@app/RuleBook/rulebook';
import { MemoryRouter } from 'react-router';
import { act } from 'react-dom/test-utils';
import { IntlProvider } from 'react-intl';
import { Route } from 'react-router-dom';
import { DropdownItem, KebabToggle, Tab } from '@patternfly/react-core';
import { mockApi } from '../__mocks__/baseApi';

const ComponentWrapper = ({ children, initialEntries = ['/dashboard'] }) => (
  <IntlProvider locale="en">
    <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
      {children}
    </MemoryRouter>
  </IntlProvider>
);

describe('RuleBook', () => {
  beforeAll(() => {
    mockApi.reset();
  });

  it('should render the RuleBook component tabs', async () => {
    mockApi.onGet(`/api/rulebooks/1`).replyOnce(200, {
      name: 'RuleBook 1',
      id: 1,
      project: { id: '1', name: 'Project 1' },
      rulesets: { id: '1', name: 'Ruleset 1' },
    });
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/rulebooks/rulebook/1']}>
          <Route path="/rulebooks/rulebook/:id">
            <RuleBook />
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

  it('has a top toolbar kebabmenu', async () => {
    mockApi.onGet(`/api/rulebooks/1`).replyOnce(200, {
      name: 'RuleBook 1',
      id: 1,
      project: { id: '1', name: 'Project 1' },
      rulesets: [{ id: '1', name: 'Ruleset 1' }],
    });
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/rulebooks/rulebook/1']}>
          <Route path="/rulebooks/rulebook/:id">
            <RuleBook />
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find(KebabToggle).length).toEqual(1);
    expect(wrapper.find('.pf-c-dropdown__toggle').length).toEqual(1);
    wrapper.find('.pf-c-dropdown__toggle').simulate('click');
    wrapper.update();
    expect(wrapper.find(DropdownItem).length).toEqual(1);
    expect(wrapper.find(DropdownItem).at(0).props().component.props.children).toEqual('Disable');
  });
});
