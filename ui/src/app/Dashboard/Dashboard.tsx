import { PageSection, Title } from '@patternfly/react-core';
import React, { useState } from 'react';
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
import styled from 'styled-components';
import {getServer} from '@app/utils/utils';
import {TopToolbar} from "@app/shared/top-toolbar";

const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`


const Dashboard: React.FunctionComponent = () => {


  return (
  <React.Fragment>

    <TopToolbar>
      <Title headingLevel={"h2"}>Dashboard</Title>
    </TopToolbar>
  </React.Fragment>
)
}

export { Dashboard };
