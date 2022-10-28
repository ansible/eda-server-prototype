import * as React from 'react';
import { mount } from 'enzyme';
import { Activation } from '@app/Activation/Activation';
import { MemoryRouter } from 'react-router';
import fetchMock from 'jest-fetch-mock';
import { act } from 'react-dom/test-utils';
import { IntlProvider } from 'react-intl';
import { Route } from 'react-router-dom';
import { DropdownItem, KebabToggle, Tab, Title } from '@patternfly/react-core';
import { ActivationDetails } from '@app/Activation/activation-details';
import { mockApi } from '../__mocks__/baseApi';

const ComponentWrapper = ({ children, initialEntries = ['/dashboard'] }) => (
  <IntlProvider locale="en">
    <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
      {children}
    </MemoryRouter>
  </IntlProvider>
);

describe('Activation', () => {
  beforeEach(() => {
    mockApi.onGet(`/api/activation_instance_job_instances/1`).replyOnce(200, {
      data: [],
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should render the Activation component tabs', async () => {
    mockApi.onGet(`/api/activation_instance/1`).replyOnce(200, {
      data: {
        name: 'Activation 1',
        id: 1,
        ruleset_id: '2',
        ruleset_name: 'Ruleset 1',
        inventory_id: '3',
        inventory_name: 'Inventory 1',
      },
    });
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/activation/1']}>
          <Route path="/activation/:id">
            <Activation />
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find(Tab).length).toEqual(4);
    expect(wrapper.find(Tab).at(0).props().title.props.children[1]).toEqual('Back to Rulebook Activations');
    expect(wrapper.find(Tab).at(1).props().title).toEqual('Details');
    expect(wrapper.find(Tab).at(2).props().title).toEqual('Jobs');
  });

  it('should render the Activation details with EDA container image', async () => {
    mockApi.onGet(`/api/activation_instance/1`).replyOnce(200, {
      data: {
        name: 'Activation 1',
        id: 1,
        ruleset_id: '2',
        ruleset_name: 'Ruleset 1',
        inventory_id: '3',
        inventory_name: 'Inventory 1',
      },
    });
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/activation/1']}>
          <Route path="/activation/:id">
            <ActivationDetails
              activation={{
                id: '1',
                name: 'Activation 1',
                description: '',
                ruleset_id: '2',
                ruleset_name: 'Ruleset 1',
                inventory_id: '3',
                inventory_name: 'Inventory 1',
              }}
            />
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find(Title).length).toEqual(13);
    expect(wrapper.find(Title).at(1).props().children).toEqual('EDA container image');
  });

  it('has a top toolbar kebab menu ', async () => {
    mockApi.onGet(`/api/activation_instance/1`).replyOnce(200, {
      data: {
        name: 'Activation 2',
        id: 1,
        ruleset_id: '2',
        ruleset_name: 'Ruleset 1',
        inventory_id: '3',
        inventory_name: 'Inventory 1',
      },
    });
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/activation/1']}>
          <Route path="/activation/:id">
            <Activation />
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
    expect(wrapper.find(DropdownItem).length).toEqual(4);
    expect(wrapper.find(DropdownItem).at(0).props().component.props.children).toEqual('Relaunch');
    expect(wrapper.find(DropdownItem).at(1).props().component.props.children).toEqual('Restart');
    expect(wrapper.find(DropdownItem).at(2).props().component.props.children).toEqual('Disable');
    expect(wrapper.find(DropdownItem).at(3).props().component.props.children).toEqual('Delete');
  });
});
