import {
  Card,
  CardBody,
  Flex,
  FlexItem,
  PageSection,
  Stack,
  StackItem,
  Title
} from '@patternfly/react-core';
import {Link, useParams} from 'react-router-dom';
import React from 'react';
import {renderRuleSetFileTabs, RuleSetType} from "@app/RuleSetFile/ruleset";
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
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.scmCredentials)}</Title></StackItem>
                <StackItem>
                  {ruleset?.scm_credentials}
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.project_link)}</Title></StackItem>
                <StackItem>
                  <Link to={"/project/" + ruleset?.project_id}>{ruleset?.project_name || `Project ${ruleset?.project_id}`}</Link>
                </StackItem>
              </Stack>
            </FlexItem>
          </Flex>
          <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.description)}</Title></StackItem>
                <StackItem>
                  {ruleset?.description}
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.number_of_rules)}</Title></StackItem>
                <StackItem>
                  { ruleset?.number_of_rules }
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.created)}</Title></StackItem>
                <StackItem>
                  {ruleset?.created_at}
                </StackItem>
              </Stack>
            </FlexItem>
          </Flex>
          <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.scmUrl)}</Title></StackItem>
                <StackItem>
                  {ruleset?.scm_url}
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.fire_count)}</Title></StackItem>
                <StackItem>
                  {ruleset?.fire_count}
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.lastModified)}</Title></StackItem>
                <StackItem>
                  {ruleset?.last_modified}
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
