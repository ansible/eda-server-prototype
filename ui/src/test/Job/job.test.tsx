import * as React from 'react';
import { mount } from 'enzyme';
import { Job } from '@app/Job/Job';
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

describe('Job', () => {
  beforeAll(() => {
    mockApi.reset();
  });

  it('has a top toolbar kebab menu', async () => {
    mockApi.onGet(`/api/job_instance/1`).replyOnce(200, {
      name: 'Job 1',
      id: 1,
      stdout: [],
    });

    mockApi.onGet(`/api/job_instance_events/1`).replyOnce(200, {
      name: 'Event 1',
      id: 1,
    });

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/job/1']}>
          <Route path="/job/:id">
            <Job />
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
    expect(wrapper.find(DropdownItem).at(1).props().component.props.children).toEqual('Launch');
    expect(wrapper.find(DropdownItem).at(2).props().component.props.children).toEqual('Delete');
  });
});
