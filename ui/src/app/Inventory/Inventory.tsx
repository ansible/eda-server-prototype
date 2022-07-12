import { PageSection, Title } from '@patternfly/react-core';
import { useParams } from 'react-router-dom';
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
import { CodeBlock, CodeBlockCode  } from '@patternfly/react-core';
import styled from 'styled-components';
import {getServer} from '@app/utils/utils';
import {TopToolbar} from "@app/shared/top-toolbar";


const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`

const endpoint = 'http://' + getServer() + '/api/inventory/';

const Inventory: React.FunctionComponent = () => {

  const [inventory, setInventory] = useState([]);

  const { id } =  useParams<Record<string, string | undefined>>()
  console.log(id);

  useEffect(() => {
     fetch(endpoint + id, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setInventory(data));
  }, []);

  return (
  <React.Fragment>
    <TopToolbar>
      <Title headingLevel={"h2"}>Inventory</Title>
    </TopToolbar>
    <CodeBlock>
      <CodeBlockCode id="code-content">{inventory.inventory}</CodeBlockCode>
    </CodeBlock>
  </React.Fragment>
)
}

export { Inventory };
