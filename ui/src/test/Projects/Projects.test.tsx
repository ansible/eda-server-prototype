import * as React from 'react';
import {mount} from 'enzyme';
import {Projects} from "@app/Projects/Projects";
import {MemoryRouter} from "react-router";
import fetchMock from "jest-fetch-mock";
import {act} from "react-dom/test-utils";
import {IntlProvider} from "react-intl";
import {Route} from "react-router-dom";
import {Button} from "@patternfly/react-core";

const ComponentWrapper = ({ children, initialEntries=['/dashboard']}) => (
  <IntlProvider locale="en">
    <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
      {children}
    </MemoryRouter>
  </IntlProvider>
);

describe('Projects', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should render the Projects component', async () => {
    fetchMock.mockResponse(JSON.stringify([{ id: '1', name: 'Project 1', url: 'Project 1 URL'},
      { id: '2', name: 'Project 2', url: 'Project 2 URL'},
      { id: '3', name: 'Project 3', url: 'Project 3 URL'} ])
    )

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/projects']}>
          <Route path='/projects'>
            <Projects/>
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper).toMatchSnapshot();
  });

  it('should have an Add button and a Delete button', async () => {
    fetchMock.mockResponse(JSON.stringify([{ id: '1', name: 'Project 1', url: 'Project 1 URL'},
      { id: '2', name: 'Project 2', url: 'Project 2 URL'},
      { id: '3', name: 'Project 3', url: 'Project 3 URL'} ])
    )

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/projects']}>
          <Route path='/projects'>
            <Projects/>
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find(Button).length).toEqual(4);
    expect(wrapper.find(Button).first().props().children).toEqual('Add project');
    expect(wrapper.find(Button).at(1).props().children).toEqual('Delete');
  });
});
