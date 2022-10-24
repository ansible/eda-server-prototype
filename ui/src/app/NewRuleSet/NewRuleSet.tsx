import { PageSection, Title } from '@patternfly/react-core';
import { useHistory } from "react-router-dom";
import React, { useState, useEffect } from 'react';
import {
  Card,
  CardBody as PFCardBody,
  SimpleList as PFSimpleList,
} from '@patternfly/react-core';
import {getServer} from '@app/utils/utils';

import styled from 'styled-components';
import {TopToolbar} from "@app/shared/top-toolbar";


const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`

const NewRuleSet: React.FunctionComponent = () => {

  const history = useHistory();

  const [value, setValue] = useState('');

  return (
    <React.Fragment>
      <TopToolbar>
        <Title headingLevel={"h2"}>New Rule Set</Title>
      </TopToolbar>

    </React.Fragment>
  )
}

export { NewRuleSet };
