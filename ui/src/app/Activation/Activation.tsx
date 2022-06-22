import * as React from 'react';
import { PageSection, Title } from '@patternfly/react-core';
import { useDispatch } from 'react-redux';
import { Link, useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import Ansi from "ansi-to-react";
import {
  Card,
  CardBody as PFCardBody,
  CardTitle,
  SimpleList as PFSimpleList,
  SimpleListItem,
  Stack,
  StackItem,
} from '@patternfly/react-core';
import styled from 'styled-components';
import {getServer} from '@app/utils/utils';


const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`


const client = new WebSocket('ws://' + getServer() + '/api/ws');

client.onopen = () => {
    console.log('Websocket client connected');
};

const endpoint1 = 'http://' + getServer() + '/api/activation/';
const endpoint2 = 'http://' + getServer() + '/api/activation_jobs/';

const Activation: React.FunctionComponent = () => {

  const [activation, setActivation] = useState([]);

  let { id } = useParams();
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
    const wc = new WebSocket('ws://' + getServer() + '/ws');
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
    const uc = new WebSocket('ws://' + getServer() + '/ws-activation/' + id);
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
  <PageSection>
    <Title headingLevel="h1" size="lg">Event Driven Automation | Activation {activation.name}</Title>
  </PageSection>
  <Link to={"/rulesetfile/" + activation.ruleset_id}>{activation.ruleset_name}</Link>
  <Link to={"/inventory/" + activation.inventory_id}>{activation.inventory_name}</Link>
  <Link to={"/var/" + activation.extravars_id}>{activation.extravars_name}</Link>
	<Stack>
            <StackItem>
              <Card>
                <CardTitle>Jobs</CardTitle>
                <CardBody>
                  {jobs.length !== 0 && (
                    <SimpleList style={{ whiteSpace: 'pre-wrap' }}>
                      {jobs.map((item, i) => (
                        <SimpleListItem key={i}><Link to={"/job/" + item.id}>{item.id} </Link></SimpleListItem>
                      ))}
                    </SimpleList>
                  )}
                </CardBody>
              </Card>
            </StackItem>
            <StackItem>
              <Card>
                <CardTitle>Standard Out</CardTitle>
                <CardBody>
                  {stdout.length !== 0 && (
                    <SimpleList style={{ whiteSpace: 'pre-wrap' }}>
                      {stdout.map((item, i) => (
                        <SimpleListItem key={i}><Ansi>{item}</Ansi></SimpleListItem>
                      ))}
                    </SimpleList>
                  )}
                </CardBody>
              </Card>
            </StackItem>
	</Stack>
  </React.Fragment>
)
}

export { Activation };
