import { Title} from '@patternfly/react-core';
import { Route, Switch, useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import AppTabs from "@app/shared/app-tabs";

import {CaretLeftIcon} from "@patternfly/react-icons";
import {getServer} from "@app/utils/utils";
import {TopToolbar} from "@app/shared/top-toolbar";
import {ActivationJobs} from "@app/Activation/activation-jobs";
import {ActivationDetails} from "@app/Activation/activation-details";
import {ActivationStdout} from "@app/Activation/activation-stdout";

export const renderActivationTabs = (activationId: string) => {
  const activation_tabs = [
    {
      eventKey: 0,
      title: (
        <>
          <CaretLeftIcon />
          {'Back to Activations'}
        </>
      ),
      name: `/activations`,
    },
    { eventKey: 1, title: 'Details', name: `/activation/${activationId}/details` },
    {
      eventKey: 2,
      title: 'Jobs',
      name: `/activation/${activationId}/jobs`,
    },
    {
      eventKey: 3,
      title: 'Standard out',
      name: `/activation/${activationId}/stdout`,
    }
  ];

  return <AppTabs tabItems={activation_tabs}/>
};

const client = new WebSocket('ws://' + getServer() + '/api/ws');
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
      <TopToolbar breadcrumbs={[
        {
          title: 'Activations',
          to: '/activations'
        }
      ]
      }>
        <Title headingLevel={"h2"}>{`${activation.name}`}</Title>
      </TopToolbar>
      <Switch>
        <Route exact path="/activation/:id/jobs">
          <ActivationJobs
            jobs={jobs}
            activation={activation}
          />
        </Route>
        <Route exact path="/activation/:id/stdout">
          <ActivationStdout
            activation={activation}
            stdout={stdout}
          />
        </Route>
        <Route path="/activation/:id">
          <ActivationDetails
            activation={activation}
          />
        </Route>
      </Switch>
    </React.Fragment>
  );
}

export { Activation };
