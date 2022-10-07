import ReducerRegistry, {
} from '@redhat-cloud-services/frontend-components-utilities/ReducerRegistry';
import { notificationsReducer } from '@redhat-cloud-services/frontend-components-notifications/redux';

const registerReducers = (registry) => {
  registry.register({
    notifications: notificationsReducer
  });
};

export default () => {
  const registry = new ReducerRegistry({}, [
        ...([])
  ]);
  registerReducers(registry);
  return registry.getStore();
};

