import { Link, useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import {
  Card,
  CardBody as PFCardBody,
  CardTitle, PageSection,
  SimpleList as PFSimpleList,
  SimpleListItem,
  Stack,
  StackItem, Title,
} from '@patternfly/react-core';
import styled from 'styled-components';
import {renderProjectTabs} from "@app/Project/Project";
import {useIntl} from "react-intl";


const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`
const ProjectLinks: React.FunctionComponent = ({project}) => {
  const intl = useIntl();
  return (
  <PageSection page-type={'project-links'} id={'project-links'}>
    { renderProjectTabs(intl, project?.id) }
    <Stack>
      <StackItem>
        <Card>
          <CardTitle>Rule Sets</CardTitle>
          <CardBody>
            {project?.rulesets.length !== 0 && (
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
            {project?.inventories.length !== 0 && (
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
            {project?.vars.length !== 0 && (
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
            {project?.playbooks.length !== 0 && (
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
