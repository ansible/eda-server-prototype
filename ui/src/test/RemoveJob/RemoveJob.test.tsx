import * as React from 'react';
import {mount} from 'enzyme';
import {MemoryRouter} from "react-router";
import fetchMock from "jest-fetch-mock";
import {act} from "react-dom/test-utils";
import {IntlProvider} from "react-intl";
import {Modal, Tab} from "@patternfly/react-core";
import {RemoveJob} from "@app/RemoveJob/RemoveJob";
import {defaultSettings} from "@app/shared/pagination";
import store from "../../store";
import {Provider} from "react-redux";

const ComponentWrapper = ({ children, initialEntries=['/dashboard']}) => (
  <Provider store={store()}>
    <IntlProvider locale="en">
      <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
        {children}
      </MemoryRouter>
    </IntlProvider>
  </Provider>
);

describe('RemoveJob', () => {
  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should render the Remove Job modal', async () => {
    fetchMock.mockResponse(JSON.stringify({
          name: 'Job 1',
          id: 1,
          url: 'Job 1 Url'
       })
    )
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/jobs/remove/1']}>
            <RemoveJob fetchData={()=>[]} pagination={defaultSettings} setSelectedJobs={()=>[]}/>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });

    expect(wrapper.find(Modal).at(0).props().title).toEqual("Delete job");
    expect(wrapper.find('Text').at(0).props().children).toEqual('Are you sure you want to delete the job below?');
    expect(wrapper.find('Text').at(1).props().children.props.children).toEqual('Job 1');
  });
})
