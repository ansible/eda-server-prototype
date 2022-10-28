import * as React from 'react';
import { mount } from 'enzyme';
import { MemoryRouter } from 'react-router';
import { act } from 'react-dom/test-utils';
import { IntlProvider } from 'react-intl';
import { Modal, Tab } from '@patternfly/react-core';
import { RemoveJob } from '@app/RemoveJob/RemoveJob';
import { defaultSettings } from '@app/shared/pagination';
import store from '../../store';
import { Provider } from 'react-redux';
import { Route } from 'react-router-dom';
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

describe('RemoveJob', () => {
  beforeAll(() => {
    mockApi.reset();
  });

  it('should render the Remove Job modal', async () => {
    mockApi.onGet(`/api/job_instance/1`).replyOnce(200, {
      name: 'Job 1',
      id: 1,
      stdout: [],
    });
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/jobs/remove/1']}>
          <Route path="/jobs/remove/:id">
            <RemoveJob fetchData={() => []} pagination={defaultSettings} resetSelectedJobs={() => []} />
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });

    expect(wrapper.find(Modal).at(0).props().title).toEqual('Delete job');
    expect(wrapper.find('Text').at(0).props().children).toEqual('Are you sure you want to delete the job below?');
    expect(wrapper.find('Text').at(1).props().children.props.children.at(1)).toEqual('Job 1');
  });

  it('should render the bulk Remove Job modal', async () => {
    mockApi.onGet(`/api/job_instances`).replyOnce(200, [
      {
        name: 'Job 1',
        id: 1,
        stdout: [],
      },
    ]);
    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/jobs/remove/1']}>
          <RemoveJob
            ids={[1, 2, 3, 4, 5, 6]}
            fetchData={() => []}
            pagination={defaultSettings}
            resetSelectedJobs={() => []}
          />
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });

    expect(wrapper.find(Modal).at(0).props().title).toEqual('Delete jobs');
    expect(wrapper.find('Text').at(0).props().children).toEqual('Are you sure you want to delete the selected jobs?');
    expect(wrapper.find('Text').at(1).props().children.props.children.at(1)).toEqual('6 selected');
  });
});
