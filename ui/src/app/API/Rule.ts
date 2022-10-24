import {getServer} from "@app/utils/utils";
import {defaultSettings} from "@app/shared/pagination";

const rulesEndpoint = 'http://' + getServer() + '/api/rules';

export const fetchRule = (ruleId, pagination=defaultSettings) =>
{
  return fetch(`${rulesEndpoint}/${ruleId}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then(response => response.json());
}

export const listRules = (pagination = defaultSettings) => fetch(rulesEndpoint, {
  headers: {
    'Content-Type': 'application/json',
  },
});
