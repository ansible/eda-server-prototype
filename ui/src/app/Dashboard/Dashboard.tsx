import { Title } from '@patternfly/react-core';
import React from 'react';
import {TopToolbar} from "@app/shared/top-toolbar";

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
