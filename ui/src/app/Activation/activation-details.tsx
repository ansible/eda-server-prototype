import {
  Card,
  CardBody,
  CodeBlock,
  CodeBlockCode,
  Flex,
  FlexItem,
  Grid,
  GridItem,
  Level,
  LevelItem,
  PageSection,
  Stack,
  StackItem,
  Title,
  ToggleGroup,
  ToggleGroupItem
} from '@patternfly/react-core';
import { CodeEditor, Language } from '@patternfly/react-code-editor';
import { Link } from 'react-router-dom';
import React, {useState, useEffect, Fragment} from 'react';
import {getServer} from '@app/utils/utils';
import {renderActivationTabs} from "@app/Activation/Activation";
import ReactJsonView from 'react-json-view';
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-yaml";
import "ace-builds/src-noconflict/theme-xcode";
import styled from 'styled-components';

const client = new WebSocket('ws://' + getServer() + '/api/ws');

client.onopen = () => {
    console.log('Websocket client connected');
};

const endpointVar = 'http://' + getServer() + '/api/extra_var/';

const FocusWrapper = styled.div`
  && + .keyboard-help-text {
    opacity: 0;
    transition: opacity 0.1s linear;
  }
  &:focus-within + .keyboard-help-text {
    opacity: 1;
  }
  & .ace_hidden-cursors .ace_cursor {
    opacity: 0;
  }
`;

const ActivationDetails: React.FunctionComponent = ({ activation }) => {

  const [activationVars, setActivationVars] = useState(undefined);
  const [varFormat, setVarFormat] = useState('yaml');
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

  const handleToggleVarFormat = (_, event) => {
    const id = event.currentTarget.id;
    setVarFormat(id );
  }

  const renderFlexActivationDetails: React.FunctionComponent = (activation) => (
    <Stack hasGutter={true}>
      <StackItem>
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
      </StackItem>
      <StackItem>
        <Stack hasGutter={true}>
          <StackItem>
            <Grid>
              <GridItem span={1}>
                <Title headingLevel="h3">Variables</Title>
              </GridItem>
              <GridItem span={2}>
                <ToggleGroup isCompact aria-label="JsonYaml">
                  <ToggleGroupItem text="YAML" buttonId="yaml" isSelected={varFormat === 'yaml' } onChange={handleToggleVarFormat} />
                  <ToggleGroupItem text="JSON" buttonId="json" isSelected={varFormat === 'json'} onChange={handleToggleVarFormat} />
                </ToggleGroup>
              </GridItem>
            </Grid>
          </StackItem>
          <StackItem>
            {activationVars ? ( varFormat === 'json' ?
                <ReactJsonView displayObjectSize={false}
                               displayDataTypes={false}
                               quotesOnKeys={false}
                               src={activationVars}/> :
                <Card>
                  <FocusWrapper>
                    <AceEditor
                      mode="javascript"
                      theme="xcode"
                      name="activation_extravars"
                      fontSize={14}
                      value={activationVars.extra_var}
                      height={'100px'}
                      setOptions={{
                        enableBasicAutocompletion: false,
                        enableLiveAutocompletion: false,
                        enableSnippets: false,
                        showLineNumbers: true,
                        tabSize: 2,
                        readOnly: true,
                        focus: false,
                        highlightActiveLine: false,
                        cursorStart: 0,
                        cursorStyle: undefined
                      }}/>
                  </FocusWrapper>
                </Card>
            ) : null
            }
          </StackItem>
        </Stack>
      </StackItem>
    </Stack>
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
