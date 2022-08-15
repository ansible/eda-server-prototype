import { Link } from 'react-router-dom';
import React from 'react';
import {
  Card,
  CardBody as PFCardBody,
  CardTitle, PageSection,
  SimpleList as PFSimpleList,
  SimpleListItem,
  Stack,
  StackItem,
} from '@patternfly/react-core';
import styled from 'styled-components';
import {renderProjectTabs} from "@app/Project/Project";
import {useIntl} from "react-intl";

interface IProject {
  id: string,
  name?: string,
  vars?: [{id: string, name: string}]
  rulesets?: [{id: string, name: string}],
  inventories?: [{id: string, name: string}],
  playbooks?: [{id: string, name: string}]
}

const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`
const ProjectLinks: React.FunctionComponent<{project:IProject | undefined}> = ({ project } : { project: IProject | undefined}) => {
  const intl = useIntl();
  return (
  <PageSection page-type={'project-links'} id={'project-links'}>
    { renderProjectTabs(intl, project?.id) }
    <Stack>
      <StackItem>
        <Card>
          <CardTitle>Rule Sets</CardTitle>
          <CardBody>
            {project?.rulesets && project.rulesets.length > 0 && (
              <SimpleList style={{ whiteSpace: 'pre-wrap' }}>
                {project.rulesets.map((item, i) => (
                  <SimpleListItem key={i}><Link to={"/rulesetfile/" + item.id}>{item.name} </Link></SimpleListItem>
                ))}
              </SimpleList>
            )}
          </CardBody>
        </Card>
      </StackItem>
      <StackItem>
        <Card>
          <CardTitle>Inventories</CardTitle>
          <CardBody>
            {project?.inventories && project.inventories.length > 0 && (
              <SimpleList style={{ whiteSpace: 'pre-wrap' }}>
                {project.inventories.map((item, i) => (
                  <SimpleListItem key={i}><Link to={"/inventory/" + item.id}>{item.name} </Link></SimpleListItem>
                ))}
              </SimpleList>
            )}
          </CardBody>
        </Card>
      </StackItem>
      <StackItem>
        <Card>
          <CardTitle>Vars</CardTitle>
          <CardBody>
            {project?.vars && project.vars.length > 0 && (
              <SimpleList style={{ whiteSpace: 'pre-wrap' }}>
                {project.vars.map((item, i) => (
                  <SimpleListItem key={i}><Link to={"/var/" + item.id}>{item.name} </Link></SimpleListItem>
                ))}
              </SimpleList>
            )}
          </CardBody>
        </Card>
      </StackItem>
      <StackItem>
        <Card>
          <CardTitle>Playbooks</CardTitle>
          <CardBody>
            {project?.playbooks && project.playbooks.length > 0 && (
              <SimpleList style={{ whiteSpace: 'pre-wrap' }}>
                {project.playbooks.map((item, i) => (
                  <SimpleListItem key={i}><Link to={"/playbook/" + item.id}>{item.name} </Link></SimpleListItem>
                ))}
              </SimpleList>
            )}
          </CardBody>
        </Card>
      </StackItem>
    </Stack>
  </PageSection>
)
}

export { ProjectLinks };
