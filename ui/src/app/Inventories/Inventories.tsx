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
import styled from 'styled-components';
import {getServer} from '@app/utils/utils';
import {TopToolbar} from "@app/shared/top-toolbar";


const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`

const endpoint = 'http://' + getServer() + '/api/inventories/';

const Inventories: React.FunctionComponent = () => {
  const [inventories, setInventories] = useState<{id: string, name: string}[]>([]);

  useEffect(() => {
     fetch(endpoint, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setInventories(data));
  }, []);

  return (
  <React.Fragment>
    <TopToolbar>
      <Title headingLevel={"h3"}> Inventories </Title>
    </TopToolbar>
    <Stack>
      <StackItem>
        <Card>
          <CardTitle>Inventories</CardTitle>
          <CardBody>
            {inventories.length !== 0 && (
              <SimpleList style={{ whiteSpace: 'pre-wrap' }}>
                {inventories.map((item, i) => (
                  <SimpleListItem key={i}><Link to={"/inventory/" + item.id}>{item.name} </Link></SimpleListItem>
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

export { Inventories };
