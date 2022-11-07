import { Title } from '@patternfly/react-core';
import { useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import { CodeBlock, CodeBlockCode } from '@patternfly/react-core';
import { TopToolbar } from '@app/shared/top-toolbar';
import { InventoryType } from '@app/RuleSets/RuleSets';
import { fetchInventory } from '@app/API/Inventory';

const Inventory: React.FunctionComponent = () => {
  const [inventory, setInventory] = useState<InventoryType | undefined>(undefined);

  const { id } = useParams<Record<string, string | undefined>>();

  useEffect(() => {
    if (!id) {
      return;
    }
    fetchInventory(id).then((data) => setInventory(data.data));
  }, [id]);

  return (
    <React.Fragment>
      <TopToolbar>
        <Title headingLevel={'h2'}>Inventory</Title>
      </TopToolbar>
      <CodeBlock>
        <CodeBlockCode id="code-content">{inventory?.inventory}</CodeBlockCode>
      </CodeBlock>
    </React.Fragment>
  );
};

export { Inventory };
