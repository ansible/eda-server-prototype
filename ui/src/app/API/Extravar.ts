import {getServer} from "@app/utils/utils";

const extravarsEndpoint = 'http://' + getServer() + '/api/extra_vars';
const extravarEndpoint = 'http://' + getServer() + '/api/extra_var';

export const listExtraVars = () => fetch(extravarsEndpoint, {
  headers: {
    'Content-Type': 'application/json',
  },
}).then(response => response.json());

export const fetchRuleVars = (varname) => {
  return fetch(extravarEndpoint + varname, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then(response => response.json())
};
