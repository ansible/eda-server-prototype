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
import { NewJob } from '@app/NewJob/NewJob';

const ComponentWrapper = ({ children, initialEntries = ['/dashboard'] }) => (
  <Provider store={store()}>
    <IntlProvider locale="en">
      <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
        {children}
      </MemoryRouter>
    </IntlProvider>
  </Provider>
);

describe('NewJob', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should render the New Job form', async () => {
    fetchMock.mockResponse(
      JSON.stringify({
        name: 'Job 1',
        id: 1,
      })
    );

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/new-job']}>
          <Route path="/new-job">
            <NewJob />
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
    expect(wrapper.find('div').at(6).at(0).props().children.at(1)).toEqual('Select a playbook');
  });
});
