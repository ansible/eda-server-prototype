import * as React from 'react';
import { mount } from 'enzyme';
import { RuleSets } from '@app/RuleSets/RuleSets';
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

describe('RuleSets', () => {
  beforeAll(() => {
    mockApi.reset();
  });

  it('should render the RuleSets component', async () => {
    mockApi.onGet(`/api/rulesets`).replyOnce(200, [
      { id: '1', name: 'RuleSet 1' },
      { id: '2', name: 'RuleSet 2' },
      { id: '3', name: 'RuleSet 3' },
    ]);

    let wrapper;
    await act(async () => {
      wrapper = mount(
        <ComponentWrapper initialEntries={['/rulesets']}>
          <Route path="/rulesets">
            <RuleSets />
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
