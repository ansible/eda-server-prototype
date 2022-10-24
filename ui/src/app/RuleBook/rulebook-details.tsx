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
import {useParams} from 'react-router-dom';
import React from 'react';
import {renderRuleBookTabs, RuleBookType} from "@app/RuleBook/rulebook";
import {useIntl} from "react-intl";
import sharedMessages from "../messages/shared.messages";

const RulebookDetails: React.FunctionComponent<{rulebook: RuleBookType}> = ({ rulebook }) => {
  const intl = useIntl();
  const {id} = useParams<{id: string}>();

  const renderFlexRulebookDetails: React.FunctionComponent<RuleBookType> = (rulebook) => (
    <Stack hasGutter={true}>
      <StackItem>
        <Flex>
          <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.name)}</Title></StackItem>
                <StackItem>
                  {rulebook?.name}
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.fire_count)}</Title></StackItem>
                <StackItem>
                  {rulebook?.fire_count}
                </StackItem>
              </Stack>
            </FlexItem>
          </Flex>
          <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.description)}</Title></StackItem>
                <StackItem>
                  {rulebook?.description}
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.created)}</Title></StackItem>
                <StackItem>
                  {rulebook?.created_at}
                </StackItem>
              </Stack>
            </FlexItem>
          </Flex>
          <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.number_of_rulesets)}</Title></StackItem>
                <StackItem>
                  { rulebook?.ruleset_count }
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.lastModified)}</Title></StackItem>
                <StackItem>
                  {rulebook?.last_modified}
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
    { renderRuleBookTabs(id, intl) }
    <Stack>
      <StackItem>
        <Card>
          <CardBody>
            {renderFlexRulebookDetails(rulebook)}
          </CardBody>
        </Card>
      </StackItem>
    </Stack>
  </PageSection>
)
}

export { RulebookDetails };
