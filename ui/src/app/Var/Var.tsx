import { Title } from '@patternfly/react-core';
import { useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import { CodeBlock, CodeBlockCode } from '@patternfly/react-core';
import { TopToolbar } from '@app/shared/top-toolbar';
import { ExtraVarType } from '@app/Vars/Vars';
import {fetchExtraVar} from "@app/API/Extravar";

const Var: React.FunctionComponent = () => {
  const [extraVar, setVar] = useState<ExtraVarType | undefined>(undefined);

  const { id } = useParams<ExtraVarType>();

  useEffect(() => {
    fetchExtraVar(id)
      .then((data) => setVar(data.data));
  }, []);

  return (
    <React.Fragment>
      <TopToolbar>
        <Title headingLevel={'h2'}>{`Var ${extraVar?.name}`}</Title>
      </TopToolbar>
      <CodeBlock>
        <CodeBlockCode id="code-content">{extraVar?.extra_var}</CodeBlockCode>
      </CodeBlock>
    </React.Fragment>
  );
};

export { Var };
