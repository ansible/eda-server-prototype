import { Title } from '@patternfly/react-core';
import { useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import { CodeBlock, CodeBlockCode  } from '@patternfly/react-core';
import {getServer} from '@app/utils/utils';
import {TopToolbar} from "@app/shared/top-toolbar";
import {InventoryType} from "@app/RuleSets/RuleSets";

const endpoint = 'http://' + getServer() + '/api/inventory/';

const Inventory: React.FunctionComponent = () => {

  const [inventory, setInventory] = useState<InventoryType|undefined>(undefined);

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
      <CodeBlockCode id="code-content">{inventory?.inventory}</CodeBlockCode>
    </CodeBlock>
  </React.Fragment>
)
}

export { Inventory };
