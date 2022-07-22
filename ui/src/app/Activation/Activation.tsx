import {PageSection, Tab, Tabs, Title} from '@patternfly/react-core';
import { Link, Route, Switch, useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import {
  Stack,
  StackItem,
} from '@patternfly/react-core';
import {getServer} from '@app/utils/utils';
import {TopToolbar} from "@app/shared/top-toolbar";
import AppTabs from "@app/shared/app-tabs";
import {ActivationDetails} from "@app/Activation/activation-details";
import {ActivationJobs} from "@app/Activation/activation-jobs";

const activation_tabs = [
  {
    eventKey: 0,
    title: 'Details',
    name: '/activation/details'
  },
  {
    eventKey: 1,
    title: 'Jobs',
    name: '/activation/jobs'
  }
];

const client = new WebSocket('ws://' + getServer() + '/api/ws');

client.onopen = () => {
    console.log('Websocket client connected');
};

const endpoint1 = 'http://' + getServer() + '/api/activation_instance/';
const endpoint2 = 'http://' + getServer() + '/api/activation_instance_job_instances/';

const Activation: React.FunctionComponent = () => {

  const [activation, setActivation] = useState([]);

  const { id } = useParams();
  console.log(id);


  useEffect(() => {
     fetch(endpoint1 + id, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setActivation(data));
  }, []);

  const [stdout, setStdout] = useState([]);
  const [newStdout, setNewStdout] = useState('');

  const [websocket_client, setWebsocketClient] = useState([]);
  useEffect(() => {
    const wc = new WebSocket('ws://' + getServer() + '/api/ws');
    setWebsocketClient(wc);
    wc.onopen = () => {
        console.log('Websocket client connected');
    };
    wc.onmessage = (message) => {
        console.log('update: ' + message.data);
        const [messageType, data] = JSON.parse(message.data);
        if (messageType === 'Stdout') {
          const { stdout: dataStdout } = data;
          setNewStdout(dataStdout);
        }
    }
  }, []);

  useEffect(() => {
    console.log(["newStdout: ",  newStdout]);
    console.log(["stdout: ",  stdout]);
    setStdout([...stdout, newStdout]);
  }, [newStdout]);

  const [jobs, setJobs] = useState([]);
  const [newJob, setNewJob] = useState([]);

  useEffect(() => {
     fetch(endpoint2 + id, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setJobs(data));
  }, []);

  const [update_client, setUpdateClient] = useState([]);
  useEffect(() => {
    const uc = new WebSocket('ws://' + getServer() + '/api/ws-activation/' + id);
    setUpdateClient(uc);
    uc.onopen = () => {
        console.log('Update client connected');
    };
    uc.onmessage = (message) => {
        console.log('update: ' + message.data);
        const [messageType, data] = JSON.parse(message.data);
        if (messageType === 'Job') {
          setNewJob(data);
        }
    }
  }, []);

  useEffect(() => {
    setJobs([...jobs, newJob]);
  }, [newJob]);

  return (
  <React.Fragment>
    <TopToolbar>
      <Title headingLevel={"h2"}>{`Activation ${activation.name}`}</Title>
    </TopToolbar>

    <Stack>
      <Tabs>
        {activation_tabs.map((item) => (
          <Tab
            title={item.title}
            key={item.eventKey}
            eventKey={item.eventKey}
            name={item.name}
            disabled={item.disabled}
          />
        ))}
      </Tabs>

      <StackItem className="pf-u-pl-lg pf-u-pr-lg pf-u-mb-lg pf-u-mt-0 pf-u-pt-0">
        <Switch>
          <Route
            path={`/activation/jobs`}
            component={ActivationJobs}
          />
          <Route path={'/activation'} component={ActivationDetails} />
        </Switch>
      </StackItem>
    </Stack>
  </React.Fragment>
)
}

export { Activation };
