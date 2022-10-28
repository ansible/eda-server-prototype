import * as React from 'react';
import { mount } from 'enzyme';
import { Project } from '@app/Project/Project';
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

describe('Project', () => {
  beforeAll(() => {
    mockApi.reset();
  });
  it('should render the Project component tabs', async () => {
    mockApi.onGet(`/api/projects/1`).replyOnce(200, {
      name: 'Project 1',
      id: 1,
      url: 'Project 1 Url',
    });
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/project/1']}>
          <Route path="/project/:id">
            <Project />
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find(Tab).length).toEqual(3);
    expect(wrapper.find(Tab).at(0).props().title.props.children[1]).toEqual('Back to Projects');
    expect(wrapper.find(Tab).at(1).props().title).toEqual('Details');
  });

  it('has a toolbar kebab menu', async () => {
    mockApi.onGet(`/api/projects/1`).replyOnce(200, {
      name: 'Project 1',
      id: 1,
      url: 'Project 1 Url',
    });
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/project/1']}>
          <Route path="/project/:id">
            <Project />
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
    expect(wrapper.find(DropdownItem).length).toEqual(3);
    expect(wrapper.find(DropdownItem).at(0).props().component.props.children).toEqual('Edit');
    expect(wrapper.find(DropdownItem).at(1).props().component.props.children).toEqual('Sync');
    expect(wrapper.find(DropdownItem).at(2).props().component.props.children).toEqual('Delete');
  });
});
