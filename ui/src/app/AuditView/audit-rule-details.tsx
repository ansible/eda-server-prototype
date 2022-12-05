import {
  Card,
  CardBody, CodeBlock, CodeBlockCode,
  Flex,
  FlexItem,
  Grid,
  GridItem,
  PageSection,
  Stack,
  StackItem,
  Text,
  TextVariants,
  Title,
  ToggleGroup,
  ToggleGroupItem,
} from '@patternfly/react-core';
import { Link, useParams } from 'react-router-dom';
import React, { useState, useEffect, Fragment } from 'react';
import ReactJsonView from 'react-json-view';
import AceEditor from 'react-ace';
import 'ace-builds/src-noconflict/mode-yaml';
import 'ace-builds/src-noconflict/theme-xcode';
import styled from 'styled-components';
import { RuleType } from '@app/RuleSets/RuleSets';
import { useIntl } from 'react-intl';
import { renderAuditRuleTabs } from '@app/AuditView/AuditRule';
import { statusLabel } from '@app/utils/utils';

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
  const [varFormat, setVarFormat] = useState('yaml');
  const intl = useIntl();
  const { id } = useParams<{ id: string }>();

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
                  <Title headingLevel="h3">Activation</Title>
                </StackItem>
                {rule && rule.activation && (
                  <StackItem>
                    <Link to={`activation/${rule.activation.id}`}>
                      {rule?.activation ? rule?.activation.name : 'Link to activation'}
                    </Link>
                  </StackItem>
                )}
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem>
                  <Title headingLevel="h3">Fired date</Title>
                </StackItem>
                <StackItem>
                  <Text component={TextVariants.small}>
                    {new Intl.DateTimeFormat('en-US', { dateStyle: 'short', timeStyle: 'long' }).format(
                      new Date(rule?.fired_date || 0)
                    )}
                  </Text>
                </StackItem>
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
                  <Title headingLevel="h3">Rule set</Title>
                </StackItem>
                {rule && rule.ruleset && (
                  <StackItem>
                    {<Link to={'/ruleset/' + rule.ruleset.id}>{rule.ruleset.name || rule.ruleset.name}</Link>}
                  </StackItem>
                )}
              </Stack>
            </FlexItem>
          </Flex>
          <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
            <FlexItem>
              <Stack>
                <StackItem>
                  <StackItem>
                    <Title headingLevel="h3">Status</Title>
                  </StackItem>
                </StackItem>
                <StackItem>
                  <Fragment key={`[audit-rule-details-${rule?.name}`}>{statusLabel({ text: rule?.status, intl: intl })}</Fragment>
                </StackItem>
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
        <Stack hasGutter>
          <StackItem>
            <Grid hasGutter>
              <GridItem span={2}>
                <Title headingLevel="h3">Rule definition</Title>
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
            {rule.definition ? (
              varFormat === 'json' ? (
                // @ts-ignore
                <ReactJsonView displayObjectSize={false} displayDataTypes={false} quotesOnKeys={false} src={rule?.definition} />
              ) : (
                <Card>
                  <FocusWrapper>
                    <AceEditor
                      mode="javascript"
                      theme="xcode"
                      name="rule_extravars"
                      fontSize={14}
                      value={JSON.stringify(rule?.definition)}
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
