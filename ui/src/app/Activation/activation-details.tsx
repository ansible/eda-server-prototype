import {CardBody, Flex, FlexItem, PageSection, Title} from '@patternfly/react-core';
import { Link, useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  DescriptionList,
  DescriptionListTerm,
  DescriptionListGroup,
  DescriptionListDescription,
  Stack,
  StackItem,
} from '@patternfly/react-core';
import {getServer} from '@app/utils/utils';
import {TopToolbar} from "@app/shared/top-toolbar";
import {renderActivationTabs} from "@app/Activation/Activation";
import ReactJsonView from 'react-json-view';

const client = new WebSocket('ws://' + getServer() + '/api/ws');

client.onopen = () => {
    console.log('Websocket client connected');
};

const endpoint1 = 'http://' + getServer() + '/api/activation_instance/';
const endpointVar = 'http://' + getServer() + '/api/extra_var/';

const ActivationDetails: React.FunctionComponent = () => {

  const [activation, setActivation] = useState([]);
  const [activationVars, setActivationVars] = useState(undefined);

  const { id } = useParams();
  console.log(id);

  const fetchActivation = (id) => {
  return fetch(endpoint1 + id, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then(response => response.json())
  };

  const fetchActivationVars = (varname) => {
    return fetch(endpointVar + varname, {
      headers: {
        'Content-Type': 'application/json',
      },
    }).then(response => response.json())
  };

  useEffect(() => {
     fetchActivation(id)
    .then(data => setActivation(data));
  }, []);

  useEffect(() => {
    activation?.extra_vars_name ? fetchActivationVars(activation.extra_vars_name)
      .then(data => setActivationVars(data)) : setActivationVars(undefined);
  }, [activation]);

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

  const [update_client, setUpdateClient] = useState([]);
  useEffect(() => {
    const uc = new WebSocket('ws://' + getServer() + '/api/ws-activation/' + id);
    setUpdateClient(uc);
    uc.onopen = () => {
        console.log('Update client connected');
    };
  }, []);

  console.log('Debug - extra vars: ', activationVars);
  const renderActivationDetails: React.FunctionComponent = (activation) => (
    <DescriptionList isFillColumns columnModifier={{ default: '3Col' }}>
      <DescriptionListGroup>
        <DescriptionListTerm>Name</DescriptionListTerm>
        <DescriptionListDescription>
          {activation?.name}
        </DescriptionListDescription>
      </DescriptionListGroup>
      <DescriptionListGroup>
        <DescriptionListTerm>Execution environment</DescriptionListTerm>
        <DescriptionListDescription>
          {activation?.execution_environment}
        </DescriptionListDescription>
      </DescriptionListGroup>
      <DescriptionListGroup>
        <DescriptionListTerm>Description</DescriptionListTerm>
        <DescriptionListDescription>
          {activation?.description}
        </DescriptionListDescription>
      </DescriptionListGroup>
      <DescriptionListGroup>
        <DescriptionListTerm>Rule set</DescriptionListTerm>
        <DescriptionListDescription><Link to={"/rulesetfile/" + activation.ruleset_id}>{activation.ruleset_name}</Link></DescriptionListDescription>
      </DescriptionListGroup>
      <DescriptionListGroup>
        <DescriptionListTerm>Inventory</DescriptionListTerm>
        <DescriptionListDescription>
          {<Link to={"/inventory/" + activation.inventory_id}>{activation.inventory_name}</Link>}
        </DescriptionListDescription>
      </DescriptionListGroup>
      <DescriptionListGroup>
        <DescriptionListTerm>Restart policy</DescriptionListTerm>
        <DescriptionListDescription>{activation?.restart_policy}</DescriptionListDescription>
      </DescriptionListGroup>
      <DescriptionListGroup>
      <DescriptionListTerm>Playbook</DescriptionListTerm>
      <DescriptionListDescription>
        {activation?.playbook}
      </DescriptionListDescription>
    </DescriptionListGroup>
     <DescriptionListGroup>
      <DescriptionListTerm>Activation status</DescriptionListTerm>
      <DescriptionListDescription>
        {activation?.status}
      </DescriptionListDescription>
    </DescriptionListGroup>
      <DescriptionListGroup>
        <DescriptionListTerm>Last restarted</DescriptionListTerm>
        <DescriptionListDescription>
          {activation?.last_restarted}
        </DescriptionListDescription>
      </DescriptionListGroup>
      <DescriptionListGroup>
        <DescriptionListTerm>Restarted count</DescriptionListTerm>
        <DescriptionListDescription>
          {activation?.restarted_count}
        </DescriptionListDescription>
      </DescriptionListGroup>
      <DescriptionListGroup>
        <DescriptionListTerm>Created</DescriptionListTerm>
        <DescriptionListDescription>
          {activation?.created_at}
        </DescriptionListDescription>
      </DescriptionListGroup>
      <DescriptionListGroup>
        <DescriptionListTerm>Last modified</DescriptionListTerm>
        <DescriptionListDescription>
          {activation?.modified_at}
        </DescriptionListDescription>
      </DescriptionListGroup>
      <DescriptionListGroup>
        <DescriptionListTerm>Variables</DescriptionListTerm>
        <DescriptionListDescription>
          {activationVars ? <ReactJsonView src={activationVars}/> : null}
        </DescriptionListDescription>
      </DescriptionListGroup>
    </DescriptionList>
  );

  const renderFlexActivationDetails: React.FunctionComponent = (activation) => (
    <Flex>
      <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
        <FlexItem>
          <Stack>
            <StackItem><Title headingLevel="h3">Name</Title></StackItem>
            <StackItem>
              {activation?.name}
            </StackItem>
          </Stack>
        </FlexItem>
        <FlexItem>
          <Stack>
            <StackItem><Title headingLevel="h3">Execution environment</Title></StackItem>
            <StackItem>
              {activation?.execution_environment}
            </StackItem>
          </Stack>
        </FlexItem>
        <FlexItem>
          <Stack>
            <StackItem><Title headingLevel="h3">Playbook</Title></StackItem>
            <StackItem>
              {activation?.playbook}
            </StackItem>
          </Stack>
        </FlexItem>
        <FlexItem>
          <Stack>
            <StackItem><Title headingLevel="h3">Restarted count</Title></StackItem>
            <StackItem>
              {activation?.restarted_count}
            </StackItem>
          </Stack>
        </FlexItem>
        <FlexItem>
          <Stack>
            <StackItem><Title headingLevel="h3">Variables</Title></StackItem>
            <StackItem>
              {activationVars ? <ReactJsonView src={activationVars}/> : null}
            </StackItem>
          </Stack>
        </FlexItem>
      </Flex>
      <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
        <FlexItem>
          <Stack>
            <StackItem><Title headingLevel="h3">Description</Title></StackItem>
            <StackItem>
              {activation?.description}
            </StackItem>
          </Stack>
        </FlexItem>
        <FlexItem>
          <Stack>
            <StackItem><Title headingLevel="h3">Rule set</Title></StackItem>
            <StackItem>
              <Link to={"/rulesetfile/" + activation.ruleset_id}>{activation.ruleset_name}</Link>
            </StackItem>
          </Stack>
        </FlexItem>
        <FlexItem>
          <Stack>
            <StackItem><Title headingLevel="h3">Activation status</Title></StackItem>
            <StackItem>
              {activation?.status}
            </StackItem>
          </Stack>
        </FlexItem>
        <FlexItem>
          <Stack>
            <StackItem><Title headingLevel="h3">Created</Title></StackItem>
            <StackItem>
              {activation?.created_at}
            </StackItem>
          </Stack>
        </FlexItem>
      </Flex>
      <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
        <FlexItem>
          <Stack>
            <StackItem><Title headingLevel="h3">Inventory</Title></StackItem>
            <StackItem>
              {<Link to={"/inventory/" + activation.inventory_id}>{activation.inventory_name}</Link>}
            </StackItem>
          </Stack>
        </FlexItem>
        <FlexItem>
          <Stack>
            <StackItem><Title headingLevel="h3">Restart policy</Title></StackItem>
            <StackItem>
              {activation?.restart_policy}
            </StackItem>
          </Stack>
        </FlexItem>
        <FlexItem>
          <Stack>
            <StackItem><Title headingLevel="h3">Last restarted</Title></StackItem>
            <StackItem>
              {activation?.last_restarted}
            </StackItem>
          </Stack>
        </FlexItem>
        <FlexItem>
          <Stack>
            <StackItem><Title headingLevel="h3">Last modified</Title></StackItem>
            <StackItem>
              {activation?.updated_at}
            </StackItem>
          </Stack>
        </FlexItem>
      </Flex>
    </Flex>
  );

  return (
  <React.Fragment>
    <TopToolbar>
      <Title headingLevel={"h2"}>{`${activation?.name}`}</Title>
    </TopToolbar>

    <PageSection page-type={'activation-details'} id={'activation-details'}>
      { renderActivationTabs(id) }
      <Stack>
        <StackItem>
          <Card>
            <CardBody>
              {renderFlexActivationDetails(activation)}
            </CardBody>
          </Card>
        </StackItem>
      </Stack>
    </PageSection>
  </React.Fragment>
)
}

export { ActivationDetails };
