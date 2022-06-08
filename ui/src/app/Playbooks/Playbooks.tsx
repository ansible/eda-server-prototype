import * as React from 'react';
import { PageSection, Title } from '@patternfly/react-core';
import { Link } from 'react-router-dom';
import { useDispatch } from 'react-redux';
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


const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`

const endpoint = 'http://' + window.location.hostname  + ':' + '8080' + '/api/playbooks/';

const Playbooks: React.FunctionComponent = () => {



  const [playbooks, setPlaybooks] = useState([]);

  useEffect(() => {
     fetch(endpoint, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setPlaybooks(data));
  }, []);

  return (
  <React.Fragment>
  <PageSection>
    <Title headingLevel="h1" size="lg">Event Driven Automation | Playbooks</Title>
  </PageSection>

	<Stack>
            <StackItem>
              <Card>
                <CardTitle>Playbooks</CardTitle>
                <CardBody>
                  {playbooks.length !== 0 && (
                    <SimpleList style={{ whiteSpace: 'pre-wrap' }}>
                      {playbooks.map((item, i) => (
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

export { Playbooks };
