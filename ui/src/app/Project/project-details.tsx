import {CardBody, Flex, FlexItem, PageSection, Title} from '@patternfly/react-core';
import React from 'react';
import {
  Card,
  Stack,
  StackItem,
} from '@patternfly/react-core';
import {extractProjectNameFromUrl, renderProjectTabs} from "@app/Project/Project";
import {useIntl} from "react-intl";
import sharedMessages from "../messages/shared.messages";

const ProjectDetails: React.FunctionComponent = ({ project }) => {
  const intl = useIntl();
  const renderFlexProjectDetails: React.FunctionComponent = (project) => (
    <Flex>
      <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
        <FlexItem>
          <Stack>
            <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.name)}</Title></StackItem>
            <StackItem>
              {project?.name || extractProjectNameFromUrl(project.url)}
            </StackItem>
          </Stack>
        </FlexItem>
        <FlexItem>
          <Stack>
            <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.scmUrl)}</Title></StackItem>
            <StackItem>
              {project?.url || ' '}
            </StackItem>
          </Stack>
        </FlexItem>
        <FlexItem>
          <Stack>
            <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.lastModified)}</Title></StackItem>
            <StackItem>
              {project?.modified_at || ' '}
            </StackItem>
          </Stack>
        </FlexItem>
      </Flex>
      <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
        <FlexItem>
          <Stack>
            <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.description)}</Title></StackItem>
            <StackItem>
              {project?.description || ' '}
            </StackItem>
          </Stack>
        </FlexItem>
        <FlexItem>
          <Stack>
            <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.scmCredentials)}</Title></StackItem>
            <StackItem>
              {project?.scm_credentials || ' '}
            </StackItem>
          </Stack>
        </FlexItem>
      </Flex>
      <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
        <FlexItem>
          <Stack>
            <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.scmType)}</Title>
              {project?.scm_type || ''}
            </StackItem>
          </Stack>
        </FlexItem>
        <FlexItem>
          <Stack>
            <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.created)}</Title></StackItem>
            <StackItem>
              {project?.created_at || ''}
            </StackItem>
          </Stack>
        </FlexItem>
      </Flex>
    </Flex>
  );

  return (
  <PageSection page-type={'project-details'} id={'project-details'}>
    { renderProjectTabs(intl, project?.id) }
    <Stack>
      <StackItem>
        <Card>
          <CardBody>
            {renderFlexProjectDetails(project)}
          </CardBody>
        </Card>
      </StackItem>
    </Stack>
  </PageSection>
)
}

export { ProjectDetails };
