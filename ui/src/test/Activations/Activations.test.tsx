import * as React from 'react';
import { mount } from 'enzyme';
import { Activations } from '@app/Activations/Activations';
import { MemoryRouter } from 'react-router';
import { act } from 'react-dom/test-utils';
import { IntlProvider } from 'react-intl';
import { Route } from 'react-router-dom';
import { mockApi } from '../__mocks__/baseApi';

const ComponentWrapper = ({ children, initialEntries = ['/dashboard'] }) => (
  <IntlProvider locale="en">
    <MemoryRouter initialEntries={initialEntries} keyLength={0} key={'test'}>
      {children}
    </MemoryRouter>
  </IntlProvider>
);

describe('Activations', () => {
  beforeAll(() => {
    mockApi.reset();
  });

  it('should render the Activations component', async () => {
    mockApi.onGet(`/api/activation_instances`).replyOnce(200, [
      { id: '1', name: 'Activation 1' },
      { id: '2', name: 'Activation 2' },
      { id: '3', name: 'Activation 3' },
    ]);

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/activations']}>
          <Route path="/activations">
            <Activations />
          </Route>
        </ComponentWrapper>
      );
    });
    await act(async () => {
      wrapper.update();
    });
    expect(wrapper).toMatchSnapshot();
  });
});
