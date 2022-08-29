import {
  Card,
  CardBody,
  Flex,
  FlexItem,
  Grid,
  GridItem,
  PageSection,
  Stack,
  StackItem,
  Title,
  ToggleGroup,
  ToggleGroupItem
} from '@patternfly/react-core';
import { Link } from 'react-router-dom';
import React, {useState, useEffect} from 'react';
import {getServer} from '@app/utils/utils';
import {renderRuleTabs} from "@app/Rule/Rule";
import ReactJsonView from 'react-json-view';
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-yaml";
import "ace-builds/src-noconflict/theme-xcode";
import styled from 'styled-components';
import {RuleType} from "@app/Rules/Rules";
import {ExtraVarType} from "@app/Vars/Vars";
import {useIntl} from "react-intl";

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

const RuleDetails: React.FunctionComponent<{rule: RuleType}> = ({ rule }) => {

  const [ruleVars, setRuleVars] = useState<ExtraVarType|undefined>(undefined);
  const [varFormat, setVarFormat] = useState('yaml');
  const id = rule?.id;
  const intl = useIntl();

  const fetchRuleVars = (varname) => {
    return fetch(endpointVar + varname, {
      headers: {
        'Content-Type': 'application/json',
      },
    }).then(response => response.json())
  };

    useEffect(() => {
    rule?.extra_var_id ? fetchRuleVars(rule.extra_var_id)
      .then(data => setRuleVars(data)) : setRuleVars(undefined);
  }, [rule]);

  const handleToggleVarFormat = (_, event) => {
    const id = event.currentTarget.id;
    setVarFormat(id );
  }

  const renderFlexRuleDetails: React.FunctionComponent<RuleType> = (rule) => (
    <Stack hasGutter={true}>
      <StackItem>
        <Flex>
          <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">Name</Title></StackItem>
                <StackItem>
                  {rule?.name}
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">Execution environment</Title></StackItem>
                <StackItem>
                  {rule?.execution_environment}
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">Playbook</Title></StackItem>
                <StackItem>
                  {rule?.playbook}
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">Restarted count</Title></StackItem>
                <StackItem>
                  {rule?.restarted_count}
                </StackItem>
              </Stack>
            </FlexItem>
          </Flex>
          <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">Description</Title></StackItem>
                <StackItem>
                  {rule?.description}
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">Rule set</Title></StackItem>
                <StackItem>
                  <Link to={"/rulesetfile/" + rule.ruleset_id}>{rule.ruleset_name}</Link>
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">Rule status</Title></StackItem>
                <StackItem>
                  {rule?.status}
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">Created</Title></StackItem>
                <StackItem>
                  {rule?.created_at}
                </StackItem>
              </Stack>
            </FlexItem>
          </Flex>
          <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">Inventory</Title></StackItem>
                <StackItem>
                  {<Link to={"/inventory/" + rule.inventory_id}>{rule.inventory_name}</Link>}
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">Restart policy</Title></StackItem>
                <StackItem>
                  {rule?.restart_policy}
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">Last restarted</Title></StackItem>
                <StackItem>
                  {rule?.last_restarted}
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">Last modified</Title></StackItem>
                <StackItem>
                  {rule?.updated_at}
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
            {ruleVars ? ( varFormat === 'json' ?
                <ReactJsonView displayObjectSize={false}
                               displayDataTypes={false}
                               quotesOnKeys={false}
                               src={ruleVars}/> :
                <Card>
                  <FocusWrapper>
                    <AceEditor
                      mode="javascript"
                      theme="xcode"
                      name="rule_extravars"
                      fontSize={14}
                      value={ruleVars?.extra_var}
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
  <PageSection page-type={'rule-details'} id={'rule-details'}>
    { renderRuleTabs(id, intl) }
    <Stack>
      <StackItem>
        <Card>
          <CardBody>
            {renderFlexRuleDetails(rule)}
          </CardBody>
        </Card>
      </StackItem>
    </Stack>
  </PageSection>
)
}

export { RuleDetails };
