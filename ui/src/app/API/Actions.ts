import { defaultSettings } from '@app/shared/pagination';
import { getAxiosInstance } from '@app/API/baseApi';
import { AxiosResponse } from 'axios';

const actionsRulesEndpoint = '/api/actions/rules_fired';
const actionsHostsEndpoint = '/api/actions/hosts_changed';
const actionsRuleEndpoint = '/api/actions/rule';

export const listActionsRules = (pagination = defaultSettings): Promise<AxiosResponse> => {
  const myPromise = new Promise<any>(function (resolve) {
    resolve({
      data: [
        {
          rule: {
            id: 1,
            name: 'Say Hello',
          },
          type: 'Playbook',
          job: {
            id: 1,
            name: 'debug',
          },
          ruleset: {
            id: 2,
            name: 'Hello Events',
          },
          status: 'successful',
          fired_date: '2022-11-17T14:54:37.813339+00:00',
        },
        {
          rule: {
            id: 1,
            name: 'Say Hi',
          },
          type: 'Job template',
          job: {
            id: 1,
            name: 'debug',
          },
          ruleset: {
            id: 2,
            name: 'Hi Events',
          },
          status: 'successful',
          fired_date: '2022-11-17T14:54:37.813339+00:00',
        },
      ],
    }); // when successful
  });
  return myPromise;
};
//getAxiosInstance().get(actionsRulesEndpoint);

export const listActionsHosts = (pagination = defaultSettings): Promise<AxiosResponse> => {
  const myPromise = new Promise<any>(function (resolve) {
    resolve({
      data: [
        {
          host: 'localhost',
          rule: {
            id: 2,
            name: 'Say Hello',
          },
          ruleset: {
            id: 2,
            name: 'Hello Events',
          },
          fired_date: '2022-11-17T14:54:37.813339+00:00',
        },
      ],
    }); // when successful
  });
  return myPromise;
};
//getAxiosInstance().get(actionsHostsEndpoint);

export const fetchActionsRuleDetails = (
  ruleId: string | number,
  pagination = defaultSettings
): Promise<AxiosResponse> => {
  const myPromise = new Promise<any>(function (resolve) {
    resolve({
      data: {
        name: 'Say Hello',
        description: null,
        status: 'successful',
        type: 'Playbook',
        activation: {
          id: 1,
          name: 'test',
        },
        ruleset: {
          id: 2,
          name: 'Hello Events',
        },
        created_at: '2022-09-26T19:19:43.679175+00:00',
        fired_date: '2022-09-26T19:19:42.216395+00:00',
        definition: {
          run_playbook: {
            name: 'benthomasson.eda.hello',
          },
        },
      },
    }); // when successful
  });
  return myPromise;
};
//getAxiosInstance().get(`${actionsRuleEndpoint}/${ruleId}/details`)

export const listActionsRuleJobs = (ruleId: string | number, pagination = defaultSettings): Promise<AxiosResponse> => {
  const myPromise = new Promise<any>(function (resolve) {
    resolve({
      data: [
        {
          id: 1,
          status: 'successful',
          last_fired_date: '2022-09-26T19:19:42.216395+00:00',
        },
      ],
    }); // when successful
  });
  return myPromise;
};
// getAxiosInstance().get(`${actionsRuleEndpoint}/${ruleId}/jobs`);

export const listActionsRuleEvents = (ruleId: string | number, pagination = defaultSettings): Promise<AxiosResponse> => {
  const myPromise = new Promise<any>(function (resolve) {
    resolve({
      data: [
        {
          id: 1,
          name: 'Say Hello',
          increment_counter: 1,
          type: 'playbook_on_start',
          timestamp: '2022-09-26T23:19:43.373381+00:00',
        },
        {
          id: 2,
          name: 'Say Hello',
          increment_counter: 2,
          type: 'playbook_on_play_start',
          timestamp: '2022-09-26T23:19:43.375731+00:00',
        },
        {
          id: 3,
          name: 'Say Hello',
          increment_counter: 3,
          type: 'playbook_on_task_start',
          timestamp: '2022-09-26T23:19:43.408264+00:00',
        },
        {
          id: 4,
          name: 'Say Hello',
          increment_counter: 4,
          type: 'runner_on_start',
          timestamp: '2022-09-26T23:19:43.409312+00:00',
        },
        {
          id: 5,
          name: 'Say Hello',
          increment_counter: 5,
          type: 'runner_on_ok',
          timestamp: '2022-09-26T23:19:43.446861+00:00',
        },
        {
          id: 6,
          name: 'Say Hello',
          increment_counter: 6,
          type: 'playbook_on_stats',
          timestamp: '2022-09-26T23:19:43.481408+00:00',
        },
      ],
    }); // when successful
  });
  return myPromise;
};
// getAxiosInstance().get(`${actionsRuleEndpoint}/${ruleId}/events`);

export const listActionsRuleHosts = (ruleId: string | number, pagination = defaultSettings): Promise<AxiosResponse> => {
  const myPromise = new Promise<any>(function (resolve) {
    resolve({
      data: [
        {
          id: 1,
          name: 'localhost',
          status: 'ok',
        },
      ],
    }); // when successful
  });
  return myPromise;
};
// getAxiosInstance().get(`${actionsRuleEndpoint}/${ruleId}/hosts`);
