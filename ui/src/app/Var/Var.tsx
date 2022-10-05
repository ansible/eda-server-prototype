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
import {TopToolbar} from "@app/shared/top-toolbar";
import {ExtraVarType} from "@app/Vars/Vars";

const endpoint = 'http://' + getServer() + '/api/extra_var/';

const Var: React.FunctionComponent = () => {

  const [extraVar, setVar] = useState<ExtraVarType|undefined>(undefined);

  const { id } = useParams<ExtraVarType>();

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
    <TopToolbar>
      <Title headingLevel={"h2"}>{`Var ${extraVar?.name}`}</Title>
    </TopToolbar>
    <CodeBlock>
      <CodeBlockCode id="code-content">{extraVar?.extra_var}</CodeBlockCode>
    </CodeBlock>
  </React.Fragment>
)
}

export { Var };
