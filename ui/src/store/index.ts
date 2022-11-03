import ReducerRegistry from '@redhat-cloud-services/frontend-components-utilities/ReducerRegistry';
import { notificationsReducer } from '@redhat-cloud-services/frontend-components-notifications/redux';
import { Store } from 'redux';

const registerReducers = (registry: ReducerRegistry): void => {
  registry.register({
    notifications: notificationsReducer,
  });
};

export default (): Store => {
  const registry = new ReducerRegistry({}, [...[]]);
  registerReducers(registry);
  return registry.getStore() as Store;
};
