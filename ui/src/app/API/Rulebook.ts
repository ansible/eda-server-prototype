import { getServer } from '@app/utils/utils';
import { defaultSettings } from '@app/shared/pagination';

const rulebooksEndpoint = 'http://' + getServer() + '/api/rulebooks';
const rulebookRulesetsEndpoint = 'http://' + getServer() + '/api/rulebook_json/';

export const listRulebooks = () =>
  fetch(rulebooksEndpoint, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then((response) => response.json());

export const fetchRulebook = (id: string | number) =>
  fetch(`${rulebooksEndpoint}/${id}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then((response) => response.json());

export const fetchRulebookRuleSets = (id, pagination = defaultSettings) => {
  return fetch(`${rulebookRulesetsEndpoint}${id}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  })
    .then((response) => response.json())
    .then((data) => (data ? data.rulesets : []));
};

export const listRuleBooks = (pagination = defaultSettings) =>
  fetch(rulebooksEndpoint, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
