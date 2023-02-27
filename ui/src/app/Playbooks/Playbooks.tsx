import { Title } from '@patternfly/react-core';
import { Link } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
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
import { PlaybookType } from '@app/RuleSets/RuleSets';

const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
`;
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`;

const endpoint = 'http://' + getServer() + '/api/playbooks';

const Playbooks: React.FunctionComponent = () => {
  const [playbooks, setPlaybooks] = useState<PlaybookType[]>([]);

  useEffect(() => {
    fetch(endpoint, {
      headers: {
        'Content-Type': 'application/json',
      },
    })
      .then((response) => response.json())
      .then((data) => setPlaybooks(data));
  }, []);

  return (
    <React.Fragment>
      <TopToolbar>
        <Title headingLevel={'h2'}>Playbooks</Title>
      </TopToolbar>
      <Stack>
        <StackItem>
          <Card>
            <CardTitle>Playbooks</CardTitle>
            <CardBody>
              {playbooks.length !== 0 && (
                <SimpleList style={{ whiteSpace: 'pre-wrap' }}>
                  {playbooks.map((item, i) => (
                    <SimpleListItem key={i}>
                      <Link to={'/playbook/' + item.id}>{item?.name} </Link>
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

export { Playbooks };
