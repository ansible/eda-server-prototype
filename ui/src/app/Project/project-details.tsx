import { CardBody, Flex, FlexItem, PageSection, Text, TextVariants, Title } from '@patternfly/react-core';
import React from 'react';
import { Card, Stack, StackItem } from '@patternfly/react-core';
import { renderProjectTabs } from '@app/Project/Project';
import { useIntl } from 'react-intl';
import sharedMessages from '../messages/shared.messages';
import { ProjectType } from '@app/shared/types/common-types';

const ProjectDetails: React.FunctionComponent<{ project: ProjectType | undefined }> = ({
  project,
}: {
  project: ProjectType | undefined;
}) => {
  const intl = useIntl();
  const renderFlexProjectDetails = (project: ProjectType | undefined): JSX.Element => (
    <Flex>
      <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
        <FlexItem>
          <Stack>
            <StackItem>
              <Title headingLevel="h3">{intl.formatMessage(sharedMessages.name)}</Title>
            </StackItem>
            <StackItem>
              <Text component={TextVariants.h4}>{project?.name || project?.url}</Text>
            </StackItem>
          </Stack>
        </FlexItem>
        <FlexItem>
          <Stack>
            <StackItem>
              <Title headingLevel="h3">{intl.formatMessage(sharedMessages.scmUrl)}</Title>
            </StackItem>
            <StackItem>
              <Text component={TextVariants.h4}>{project?.url || ' '}</Text>
            </StackItem>
          </Stack>
        </FlexItem>
        <FlexItem>
          <Stack>
            <StackItem>
              <Title headingLevel="h5">{intl.formatMessage(sharedMessages.lastModified)}</Title>
            </StackItem>
            <StackItem>
              <Text component={TextVariants.h3}>
                {new Intl.DateTimeFormat('en-US', { dateStyle: 'short', timeStyle: 'long' }).format(
                  new Date(project?.modified_at || 0)
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
              <Title headingLevel="h3">{intl.formatMessage(sharedMessages.description)}</Title>
            </StackItem>
            <StackItem>
              <Text component={TextVariants.h4}>{project?.description || ' '}</Text>
            </StackItem>
          </Stack>
        </FlexItem>
        <FlexItem>
          <Stack>
            <StackItem>
              <Title headingLevel="h3">{intl.formatMessage(sharedMessages.scmToken)}</Title>
            </StackItem>
            <StackItem>
              <Text component={TextVariants.h4}>{project?.scm_token || ' '}</Text>
            </StackItem>
          </Stack>
        </FlexItem>
      </Flex>
      <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
        <FlexItem>
          <Stack>
            <StackItem>
              <Title headingLevel="h3">{intl.formatMessage(sharedMessages.scmType)}</Title>
              <Text component={TextVariants.h4}>{project?.scm_type || ''}</Text>
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
                {new Intl.DateTimeFormat('en-US', { dateStyle: 'short', timeStyle: 'long' }).format(
                  new Date(project?.created_at || 0)
                )}
              </Text>
            </StackItem>
          </Stack>
        </FlexItem>
      </Flex>
    </Flex>
  );

  return (
    <PageSection page-type={'project-details'} id={'project-details'}>
      {renderProjectTabs(project?.id || '', intl)}
      <Stack>
        <StackItem>
          <Card>
            <CardBody>{renderFlexProjectDetails(project)}</CardBody>
          </Card>
        </StackItem>
      </Stack>
    </PageSection>
  );
};

export { ProjectDetails };
