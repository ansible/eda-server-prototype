import * as React from 'react';
import {mount} from 'enzyme';
import {MemoryRouter} from "react-router";
import fetchMock from "jest-fetch-mock";
import {act} from "react-dom/test-utils";
import {IntlProvider} from "react-intl";
import {Modal, Tab} from "@patternfly/react-core";
import {RemoveProject} from "@app/RemoveProject/RemoveProject";
import {defaultSettings} from "@app/shared/pagination";
import store from '../../store'
import {Provider} from "react-redux";
import {Route} from "react-router-dom";

const ComponentWrapper = ({ children, initialEntries=['/dashboard']}) => (
  <Provider store={store()}>
    <IntlProvider locale="en">
      <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
        {children}
      </MemoryRouter>
    </IntlProvider>
  </Provider>
);

describe('RemoveProject', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should render the Remove Project modal', async () => {
    fetchMock.mockResponse(JSON.stringify({
          name: 'Project 1',
          id: 1,
          url: 'Project 1 Url'
       })
    )
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/projects/remove/1']}>
          <Route path='/projects/remove/:id'>
            <RemoveProject fetchData={()=>[]} pagination={defaultSettings} resetSelectedProjects={()=>[]}/>
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });

    expect(wrapper.find(Modal).at(0).props().title).toEqual("Delete project");
    expect(wrapper.find('Text').at(0).props().children).toEqual('Are you sure you want to delete the project below?');
    expect(wrapper.find('Text').at(1).props().children.props.children.at(1)).toEqual('Project 1');
  });

  it('should render the bulk Remove Project modal', async () => {
    fetchMock.mockResponse(JSON.stringify({
        name: 'Project 1',
        id: 1,
        url: 'Project 1 Url'
      })
    )
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/projects/remove/1']}>
          <RemoveProject ids={[1,2,3]} fetchData={()=>[]} pagination={defaultSettings} resetSelectedProjects={()=>[]}/>
         </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });

    expect(wrapper.find(Modal).at(0).props().title).toEqual("Delete selected projects");
    expect(wrapper.find('Text').at(0).props().children).toEqual('Are you sure you want to delete the selected projects?');
    expect(wrapper.find('Text').at(1).props().children.props.children.at(1)).toEqual('3 selected');
  });
})
