import * as React from 'react';
import {mount} from 'enzyme';
import {MemoryRouter} from "react-router";
import fetchMock from "jest-fetch-mock";
import {act} from "react-dom/test-utils";
import {IntlProvider} from "react-intl";
import {Route} from "react-router-dom";
import {Button, Tab, TextInput} from "@patternfly/react-core";
import store from "../../store";
import {Provider} from "react-redux";
import {NewProject} from "@app/NewProject/NewProject";

const ComponentWrapper = ({ children, initialEntries=['/dashboard']}) => (
  <Provider store={store()}>
    <IntlProvider locale="en">
      <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
        {children}
      </MemoryRouter>
    </IntlProvider>
  </Provider>
);

describe('NewProject', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should render the NewProject form', async () => {
    fetchMock.mockResponse(JSON.stringify({
          name: 'Project 1',
          id: 1,
          url: 'test.com'
      })
    )

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/new-project']}>
          <Route path='/new-project'>
            <NewProject/>
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
    expect(wrapper.find('div').at(8).at(0).props().children.at(1)).toEqual('Enter project name')
  });

  it('should switch to the Adding button on commit', async () => {
    fetchMock.mockResponse(JSON.stringify({
        name: 'Project 1',
        id: 1,
        url: 'test.com'
      })
    )

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/new-project']}>
          <Route path='/new-project'>
            <NewProject/>
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });

    let inputName = wrapper.find(TextInput).at(0);
    inputName.getDOMNode().value = 'Project';
    inputName.simulate('change');
    let inputUrl = wrapper.find(TextInput).at(3);
    inputUrl.getDOMNode().value = 'project@test.com';
    inputUrl.simulate('change');

    expect(wrapper.find(Button).length).toEqual(2);
    wrapper.find(Button).at(0).simulate('click');
    expect(wrapper.find(Button).at(0).props().isLoading).toBeTruthy();
  });
});
