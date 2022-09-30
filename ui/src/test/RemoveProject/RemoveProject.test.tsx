import * as React from 'react';
import {mount} from 'enzyme';
import {MemoryRouter} from "react-router";
import fetchMock from "jest-fetch-mock";
import {act} from "react-dom/test-utils";
import {IntlProvider} from "react-intl";
import {Modal, Tab} from "@patternfly/react-core";
import {RemoveProject} from "@app/RemoveProject/RemoveProject";
import {defaultSettings} from "@app/shared/pagination";

const ComponentWrapper = ({ children, initialEntries=['/dashboard']}) => (
  <IntlProvider locale="en">
    <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
      {children}
    </MemoryRouter>
  </IntlProvider>
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
            <RemoveProject fetchData={()=>[]} pagination={defaultSettings} setSelectedProjects={()=>[]}/>
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
})
