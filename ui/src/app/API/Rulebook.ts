import {getServer} from "@app/utils/utils";

const rulebooksEndpoint = 'http://' + getServer() + '/api/rulebooks';

export const listRulebooks = () => fetch(rulebooksEndpoint, {
  headers: {
    'Content-Type': 'application/json',
  },
}).then(response => response.json())
