import {
  Card,
  CardBody,
  Flex,
  FlexItem,
  PageSection,
  Stack,
  StackItem, Text, TextVariants,
  Title
} from '@patternfly/react-core';
import {Link, useParams} from 'react-router-dom';
import React from 'react';
import {renderRuleSetFileTabs, RuleSetType} from "@app/RuleSet/ruleset";
import {useIntl} from "react-intl";
import sharedMessages from "../messages/shared.messages";

const RulesetDetails: React.FunctionComponent<{ruleset: RuleSetType}> = ({ ruleset }) => {
  const intl = useIntl();
  const {id} = useParams<{id: string}>();

  const renderFlexRulesetDetails: React.FunctionComponent<RuleSetType> = (ruleset) => (
    <Stack hasGutter={true}>
      <StackItem>
        <Flex>
          <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.name)}</Title></StackItem>
                <StackItem>
                  {ruleset?.name}
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.number_of_rules)}</Title></StackItem>
                <StackItem>
                  {ruleset?.rule_count}
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem>
                  <Title headingLevel="h3">{intl.formatMessage(sharedMessages.lastModified)}</Title>
                </StackItem>
                <StackItem>
                  <Text component={TextVariants.h5}>
                    {new Intl.DateTimeFormat('en-US',
                      { dateStyle: 'short', timeStyle: 'long' }).format(new Date(ruleset?.modified_at || 0))}
                  </Text>
                </StackItem>
              </Stack>
            </FlexItem>
          </Flex>
          <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
            <FlexItem>
              <Stack>
                <StackItem>
                  <Title headingLevel="h3">{intl.formatMessage(sharedMessages.description)}</Title>
                </StackItem>
                <StackItem>
                  {ruleset?.description}
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem>
                  <Title headingLevel="h3">{intl.formatMessage(sharedMessages.project_link)}</Title>
                </StackItem>
                <StackItem>
                  <Link to={"/project/" + ruleset?.project?.id}>{ruleset?.project?.name
                    || `Project ${ruleset?.project?.id}`}</Link>
                </StackItem>
              </Stack>
            </FlexItem>
          </Flex>
          <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
            <FlexItem>
              <Stack>
                <StackItem>
                  <Title headingLevel="h3">{intl.formatMessage(sharedMessages.rulebook)}</Title>
                </StackItem>
                <StackItem>
                  <Link to={"/rulebooks/rulebook/" + ruleset?.rulebook?.id}>{ruleset?.rulebook?.name
                    || `Project ${ruleset?.rulebook?.id}`}</Link>
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem>
                  <Title headingLevel="h3">{intl.formatMessage(sharedMessages.created)}</Title>
                </StackItem>
                <StackItem>
                  <Text component={TextVariants.h5}>
                    {new Intl.DateTimeFormat('en-US',
                      { dateStyle: 'short', timeStyle: 'long' }).format(new Date(ruleset?.created_at || 0))}
                  </Text>
                </StackItem>
              </Stack>
            </FlexItem>
          </Flex>
        </Flex>
        </StackItem>
     </Stack>
  );

  return (
  <PageSection page-type={'ruleset-details'} id={'ruleset-details'}>
    { renderRuleSetFileTabs(id, intl) }
    <Stack>
      <StackItem>
        <Card>
          <CardBody>
            {renderFlexRulesetDetails(ruleset)}
          </CardBody>
        </Card>
      </StackItem>
    </Stack>
  </PageSection>
)
}

export { RulesetDetails };
