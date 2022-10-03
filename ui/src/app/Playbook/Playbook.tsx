import { PageSection, Title } from '@patternfly/react-core';
import { useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import { CodeBlock, CodeBlockCode  } from '@patternfly/react-core';
import {getServer} from '@app/utils/utils';
import {TopToolbar} from "@app/shared/top-toolbar";
import {PlaybookType} from "@app/RuleSets/RuleSets";

const endpoint = 'http://' + getServer() + '/api/playbook/';

const Playbook: React.FunctionComponent = () => {

  const [playbook, setPlaybook] = useState<PlaybookType|undefined>(undefined);

  const { id } = useParams<{id:string}>();
  console.log(id);

  useEffect(() => {
     fetch(endpoint + id, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setPlaybook(data));
  }, []);

  return (
  <React.Fragment>
    <TopToolbar>
      <Title headingLevel={"h2"}>{`Playbook ${playbook?.name}`}</Title>
    </TopToolbar>
    <CodeBlock>
      <CodeBlockCode id="code-content">{playbook?.playbook}</CodeBlockCode>
    </CodeBlock>
  </React.Fragment>
)
}

export { Playbook };
