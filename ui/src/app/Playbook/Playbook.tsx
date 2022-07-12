import { PageSection, Title } from '@patternfly/react-core';
import { useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import { CodeBlock, CodeBlockCode  } from '@patternfly/react-core';
import {getServer} from '@app/utils/utils';
import {TopToolbar} from "@app/shared/top-toolbar";

const endpoint = 'http://' + getServer() + '/api/playbook/';

const Playbook: React.FunctionComponent = () => {

  const [playbook, setPlaybook] = useState([]);

  const { id } = useParams();
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
      <Title headingLevel={"h2"}>{`Playbook ${playbook.url}`}</Title>
    </TopToolbar>
    <CodeBlock>
      <CodeBlockCode id="code-content">{playbook.playbook}</CodeBlockCode>
    </CodeBlock>
  </React.Fragment>
)
}

export { Playbook };
