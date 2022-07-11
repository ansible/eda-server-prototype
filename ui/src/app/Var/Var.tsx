import * as React from 'react';
import { PageSection, Title } from '@patternfly/react-core';
import { useDispatch } from 'react-redux';
import { Link, useParams } from 'react-router-dom';
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
import { CodeBlock, CodeBlockCode  } from '@patternfly/react-core';
import styled from 'styled-components';
import {getServer} from '@app/utils/utils';


const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`

const endpoint = 'http://' + getServer() + '/api/extra_var/';

const Var: React.FunctionComponent = () => {

  const [extraVar, setVar] = useState([]);

  const { id } = useParams();
  console.log(id);

  useEffect(() => {
     fetch(endpoint + id, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setVar(data));
  }, []);

  return (
  <React.Fragment>
  <PageSection>
    <Title headingLevel="h1" size="lg">Event Driven Automation | Var {extraVar.name}</Title>
  </PageSection>
    <CodeBlock>
      <CodeBlockCode id="code-content">{extraVar.extra_var}</CodeBlockCode>
    </CodeBlock>
  </React.Fragment>
)
}

export { Var };
