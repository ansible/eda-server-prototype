import * as React from 'react';
import { mount } from 'enzyme';
import { MemoryRouter } from 'react-router';
import { act } from 'react-dom/test-utils';
import { IntlProvider } from 'react-intl';
import { Route } from 'react-router-dom';
import { Button, TextInput } from '@patternfly/react-core';
import store from '../../store';
import { Provider } from 'react-redux';
import { NewProject } from '@app/NewProject/NewProject';
import { mockApi } from '../__mocks__/baseApi';

const ComponentWrapper = ({ children, initialEntries = ['/dashboard'] }) => (
  <Provider store={store()}>
    <IntlProvider locale="en">
      <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
        {children}
      </MemoryRouter>
    </IntlProvider>
  </Provider>
);

describe('NewProject', () => {
  beforeAll(() => {
    mockApi.reset();
  });

  it('should render the NewProject form', async () => {
    mockApi.onPost(`/api/projects`).replyOnce(200, {
      name: 'Project 1',
      id: 1,
      url: 'test.com',
    });

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/new-project']}>
          <Route path="/new-project">
            <NewProject />
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
    expect(wrapper.find('div').at(8).at(0).props().children.at(1)).toEqual('Enter project name');
  });

  it('should switch to the Adding button on commit', async () => {
    mockApi.onPost(`/api/projects`).replyOnce(200, {
      name: 'Project 1',
      id: 1,
      url: 'test.com',
    });

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/new-project']}>
          <Route path="/new-project">
            <NewProject />
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });

    const inputName = wrapper.find(TextInput).at(0);
    inputName.getDOMNode().value = 'Project';
    inputName.simulate('change');
    const inputUrl = wrapper.find(TextInput).at(3);
    inputUrl.getDOMNode().value = 'project@test.com';
    inputUrl.simulate('change');

    expect(wrapper.find(Button).length).toEqual(2);
    wrapper.find(Button).at(0).simulate('click');
    expect(wrapper.find(Button).at(0).props().isLoading).toBeTruthy();
  });
});
