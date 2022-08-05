import {CardBody, Flex, FlexItem, PageSection, Title} from '@patternfly/react-core';
import { Link } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import {
  Card,
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

const endpointVar = 'http://' + getServer() + '/api/extra_var/';

const ActivationDetails: React.FunctionComponent = ({ activation }) => {

  const [activationVars, setActivationVars] = useState(undefined);
  const id = activation?.id;
  console.log(id);

  const fetchActivationVars = (varname) => {
    return fetch(endpointVar + varname, {
      headers: {
        'Content-Type': 'application/json',
      },
    }).then(response => response.json())
  };

    useEffect(() => {
    activation?.extra_var_id ? fetchActivationVars(activation.extra_var_id)
      .then(data => setActivationVars(data)) : setActivationVars(undefined);
  }, [activation]);
  console.log('Debug - extra vars: ', activationVars);

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
              {activationVars ? <ReactJsonView displayObjectSize={false}
                                               displayDataTypes={false}
                                               quotesOnKeys={false}
                                               src={activationVars}/> : null}
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
)
}

export { ActivationDetails };
