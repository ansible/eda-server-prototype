import * as React from 'react';
import {mount} from 'enzyme';
import {Project} from "@app/Project/Project";
import {MemoryRouter} from "react-router";
import fetchMock from "jest-fetch-mock";
import {act} from "react-dom/test-utils";
import {IntlProvider} from "react-intl";
import {Route} from "react-router-dom";
import {Tab} from "@patternfly/react-core";
import {CaretLeftIcon} from "@patternfly/react-icons";

const ComponentWrapper = ({ children, initialEntries=['/dashboard']}) => (
  <IntlProvider locale="en">
    <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
      {children}
    </MemoryRouter>
  </IntlProvider>
);

describe('Project', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should render the Project component tabs', async () => {
    fetchMock.mockResponse(JSON.stringify({
          name: 'Project 1',
          id: 1,
          url: 'Project 1 Url'
       })
    )
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/project/1']}>
          <Route path='/project/:id'>
            <Project/>
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper.find(Tab).length).toEqual(3);
    expect(wrapper.find(Tab).at(0).props().title.props.children[1]).toEqual("Back to projects");
    expect(wrapper.find(Tab).at(1).props().title).toEqual('Details');
  });
});
