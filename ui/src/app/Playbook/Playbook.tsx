import { PageSection, Title } from '@patternfly/react-core';
import { useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import { CodeBlock, CodeBlockCode  } from '@patternfly/react-core';
import {getServer} from '@app/utils/utils';

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
  <PageSection>
    <Title headingLevel="h1" size="lg">Event Driven Automation | Playbook {playbook.url}</Title>
  </PageSection>
    <CodeBlock>
      <CodeBlockCode id="code-content">{playbook.playbook}</CodeBlockCode>
    </CodeBlock>
  </React.Fragment>
)
}

export { Playbook };
