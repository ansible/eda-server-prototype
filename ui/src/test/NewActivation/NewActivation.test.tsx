import * as React from 'react';
import { mount } from 'enzyme';
import { MemoryRouter } from 'react-router';
import fetchMock from 'jest-fetch-mock';
import { act } from 'react-dom/test-utils';
import { IntlProvider } from 'react-intl';
import { Route } from 'react-router-dom';
import { Button } from '@patternfly/react-core';
import store from '../../store';
import { Provider } from 'react-redux';
import { NewActivation } from '@app/NewActivation/NewActivation';

const ComponentWrapper = ({ children, initialEntries = ['/dashboard'] }) => (
  <Provider store={store()}>
    <IntlProvider locale="en">
      <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
        {children}
      </MemoryRouter>
    </IntlProvider>
  </Provider>
);

describe('NewActivation', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should render the NewActivation form', async () => {
    fetchMock.mockResponse(
      JSON.stringify({
        name: 'Activation 1',
        id: 1,
        ruleset_id: '2',
        ruleset_name: 'Ruleset 1',
        inventory_id: '3',
        inventory_name: 'Inventory 1',
      })
    );

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/new-activation']}>
          <Route path="/new-activation">
            <NewActivation />
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find(Button).length).toEqual(2);
    wrapper.find(Button).at(0).simulate('click');
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find('div').at(8).at(0).props().children.at(1)).toEqual('Enter a rulebook activation name');
  });
});
