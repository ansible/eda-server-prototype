import * as React from 'react';
import { PageSection, Title } from '@patternfly/react-core';
import { useDispatch } from 'react-redux';
import { Link, useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import Ansi from "ansi-to-react";
import {
  Card,
  CardBody as PFCardBody,
  CardTitle,
  SimpleList as PFSimpleList,
  SimpleListItem,
  Stack,
  StackItem,
} from '@patternfly/react-core';
import styled from 'styled-components';
import {getServer} from '@app/utils/utils';


const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`

const endpoint = 'http://' + getServer() + '/api/project/';

const Project: React.FunctionComponent = () => {

  const [project, setProject] = useState({'rulesets': [],
                                          'inventories': [],
                                          'vars': [],
                                          'playbooks': []});

  let { id } = useParams();
  console.log(id);

  useEffect(() => {
     fetch(endpoint + id, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setProject(data));
  }, []);

  return (
  <React.Fragment>
  <PageSection>
    <Title headingLevel="h1" size="lg">Event Driven Automation | Project {project.url}</Title>
  </PageSection>

	<Stack>

            <StackItem>
              <Card>
                <CardTitle>Rule Sets</CardTitle>
                <CardBody>
                  {project.rulesets.length !== 0 && (
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
                  {project.inventories.length !== 0 && (
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
                  {project.vars.length !== 0 && (
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
                  {project.playbooks.length !== 0 && (
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
  </React.Fragment>
)
}

export { Project };
