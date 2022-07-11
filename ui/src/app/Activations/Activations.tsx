import { PageSection, Title } from '@patternfly/react-core';
import { Link } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import {
  Card,
  CardBody as PFCardBody,
  CardTitle,
  SimpleList as PFSimpleList,
  SimpleListItem,
  Stack,
  StackItem,
} from '@patternfly/react-core';
import { Button } from '@patternfly/react-core';
import PlusCircleIcon from '@patternfly/react-icons/dist/esm/icons/plus-circle-icon';
import styled from 'styled-components';
import {getServer} from '@app/utils/utils';


const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`

const endpoint = 'http://' + getServer()+ '/api/activation_instances/';

const Activations: React.FunctionComponent = () => {


  const [activations, setActivations] = useState([]);

  useEffect(() => {
     fetch(endpoint, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setActivations(data));
  }, []);

  return (
  <React.Fragment>
  <PageSection>
    <Title headingLevel="h1" size="lg">Event Driven Automation | Activations</Title>
  </PageSection>

  <Link to="/new-activation">
  <Button variant="link" icon={<PlusCircleIcon />}>
      New Activation
  </Button>
  </Link>
	<Stack>
            <StackItem>
              <Card>
                <CardTitle>Activations</CardTitle>
                <CardBody>
                  {activations.length !== 0 && (
                    <SimpleList style={{ whiteSpace: 'pre-wrap' }}>
                      {activations.map((item, i) => (
                        <SimpleListItem key={i}><Link to={"/activation/" + item.id}>{item.name} </Link></SimpleListItem>
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

export { Activations };
