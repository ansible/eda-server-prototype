import {getServer} from "@app/utils/utils";

const vars_endpoint = 'http://' + getServer() + '/api/extra_vars';

export const listExtraVars = () => fetch(vars_endpoint, {
  headers: {
    'Content-Type': 'application/json',
  },
}).then(response => response.json());
