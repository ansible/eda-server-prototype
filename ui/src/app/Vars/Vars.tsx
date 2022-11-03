import React, { useState, useEffect } from 'react';
import { Title } from '@patternfly/react-core';
import { Link } from 'react-router-dom';
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
import { getServer } from '@app/utils/utils';
import { TopToolbar } from '@app/shared/top-toolbar';

export interface ExtraVarType {
  id: string;
  name: string;
  extra_var: string;
}

const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
`;
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`;
const endpoint = 'http://' + getServer() + '/api/extra_vars/';

const Vars: React.FunctionComponent = () => {
  const [extraVars, setVars] = useState<ExtraVarType[]>([]);

  useEffect(() => {
    fetch(endpoint, {
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then((response) => response.json())
      .then((data) => setVars(data));
  }, []);

  return (
    <React.Fragment>
      <TopToolbar>
        <Title headingLevel={'h2'}>Extra vars</Title>
      </TopToolbar>
      <Stack>
        <StackItem>
          <Card>
            <CardTitle>Extra Vars</CardTitle>
            <CardBody>
              {extraVars.length !== 0 && (
                <SimpleList style={{ whiteSpace: 'pre-wrap' }}>
                  {extraVars.map((item, i) => (
                    <SimpleListItem key={i}>
                      <Link to={'/var/' + item.id}>{item.name} </Link>
                    </SimpleListItem>
                  ))}
                </SimpleList>
              )}
            </CardBody>
          </Card>
        </StackItem>
      </Stack>
    </React.Fragment>
  );
};

export { Vars };
