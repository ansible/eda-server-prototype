import * as React from 'react';
import { mount } from 'enzyme';
import { InventoriesSelect } from '@app/InventoriesSelect/InventoriesSelect';
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

describe('InventoriesSelect', () => {
  beforeAll(() => {
    mockApi.reset();
  });

  it('should render the InventoriesSelect component', async () => {
    mockApi.onGet(`/api/InventoriesSelect`).replyOnce(200, [
      { id: '1', name: 'Inventory 1' },
      { id: '2', name: 'Inventory 2' },
      { id: '3', name: 'Inventory 3' },
    ]);

    let wrapper;
    const inventory = undefined;
    const setInventory = (inventory) => undefined;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/InventoriesSelect']}>
          <Route path="/InventoriesSelect">
            <InventoriesSelect
              inventory={inventory}
              setInventory={setInventory}
              isModalOpen={true}
              setIsModalOpen={() => true}
            />
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
