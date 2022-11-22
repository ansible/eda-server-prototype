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
  ToggleGroupItem,
} from '@patternfly/react-core';
import { Link } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import ReactJsonView from 'react-json-view';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/mode-yaml';
import 'ace-builds/src-noconflict/theme-xcode';
import styled from 'styled-components';
import { RuleType } from '@app/RuleSets/RuleSets';
import { ExtraVarType } from '@app/Vars/Vars';
import { useIntl } from 'react-intl';
import { fetchRuleVars } from '@app/API/Extravar';
import {renderAuditRuleTabs} from "@app/AuditView/AuditRule";

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

const AuditRuleDetails: React.FunctionComponent<{ rule: RuleType }> = ({ rule }) => {
  const [ruleVars, setRuleVars] = useState<ExtraVarType | undefined>(undefined);
  const [varFormat, setVarFormat] = useState('yaml');
  const id = rule?.id;
  const intl = useIntl();

  useEffect(() => {
    rule?.extra_var_id
      ? fetchRuleVars(rule.extra_var_id).then((data) => setRuleVars(data?.data))
      : setRuleVars(undefined);
  }, [rule]);

  const handleToggleVarFormat = (_, event) => {
    const id = event.currentTarget.id;
    setVarFormat(id);
  };

  const renderFlexRuleDetails: React.FunctionComponent<RuleType> = (rule) => (
    <Stack hasGutter={true}>
      <StackItem>
        <Flex>
          <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
            <FlexItem>
              <Stack>
                <StackItem>
                  <Title headingLevel="h3">Name</Title>
                </StackItem>
                <StackItem>{rule?.name}</StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem>
                  <Title headingLevel="h3">Action</Title>
                </StackItem>
                {rule && rule.action && (
                  <StackItem>
                    <Link to={'/jobs'}>{rule?.action ? Object.keys(rule?.action) : 'Link to action'}</Link>
                  </StackItem>
                )}
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem>
                  <Title headingLevel="h3">Last fired date</Title>
                </StackItem>
                <StackItem>{rule?.last_fired_date}</StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem>
                  <Title headingLevel="h3">Last modified</Title>
                </StackItem>
                <StackItem>{rule?.modified_at}</StackItem>
              </Stack>
            </FlexItem>
          </Flex>
          <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
            <FlexItem>
              <Stack>
                <StackItem>
                  <Title headingLevel="h3">Description</Title>
                </StackItem>
                <StackItem>{rule?.description}</StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem>
                  <Title headingLevel="h3">Project</Title>
                </StackItem>
                {rule && rule.project_id && (
                  <StackItem>
                    <Link to={'/project/' + rule?.project_id}>
                      {rule?.project_name || `Project ${rule?.project_id}`}
                    </Link>
                  </StackItem>
                )}
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem>
                  <Title headingLevel="h3">Fire count</Title>
                </StackItem>
                <StackItem>{rule?.fired_count || 0}</StackItem>
              </Stack>
            </FlexItem>
          </Flex>
          <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
            <FlexItem>
              <Stack>
                <StackItem>
                  <Title headingLevel="h3">Rule set</Title>
                </StackItem>
                {rule && rule.ruleset && (
                  <StackItem>
                    {<Link to={'/ruleset/' + rule.ruleset.id}>{rule.ruleset.name || rule.ruleset.name}</Link>}
                  </StackItem>
                )}
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem>
                  <Title headingLevel="h3">Rule type</Title>
                </StackItem>
                <StackItem>{rule?.type}</StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem>
                  <Title headingLevel="h3">Created</Title>
                </StackItem>
                <StackItem>{rule?.created_at}</StackItem>
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
                  <ToggleGroupItem
                    text="YAML"
                    buttonId="yaml"
                    isSelected={varFormat === 'yaml'}
                    onChange={handleToggleVarFormat}
                  />
                  <ToggleGroupItem
                    text="JSON"
                    buttonId="json"
                    isSelected={varFormat === 'json'}
                    onChange={handleToggleVarFormat}
                  />
                </ToggleGroup>
              </GridItem>
            </Grid>
          </StackItem>
          <StackItem>
            {ruleVars ? (
              varFormat === 'json' ? (
                <ReactJsonView displayObjectSize={false} displayDataTypes={false} quotesOnKeys={false} src={ruleVars} />
              ) : (
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
                        cursorStyle: undefined,
                      }}
                    />
                  </FocusWrapper>
                </Card>
              )
            ) : null}
          </StackItem>
        </Stack>
      </StackItem>
    </Stack>
  );

  return (
    <PageSection page-type={'rule-details'} id={'rule-details'}>
      {renderAuditRuleTabs(id, intl)}
      <Stack>
        <StackItem>
          <Card>
            <CardBody>{renderFlexRuleDetails(rule)}</CardBody>
          </Card>
        </StackItem>
      </Stack>
    </PageSection>
  );
};

export { AuditRuleDetails };
