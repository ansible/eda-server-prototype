import {defaultSettings} from "@app/shared/pagination";
import {getServer} from "@app/utils/utils";

const playbooksEndpoint = 'http://' + getServer() + '/api/playbooks/';

export const listPlaybooks = (pagination=defaultSettings) => fetch(playbooksEndpoint, {
  headers: {
    'Content-Type': 'application/json',
  },
}).then(response => response.json())
