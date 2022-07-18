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


const client = new WebSocket('ws://' + getServer() + '/api/ws');

client.onopen = () => {
    console.log('Websocket client connected');
};


const Dashboard: React.FunctionComponent = () => {


  const [stdout, setStdout] = useState<never[]>([]);


  client.onmessage = (message) => {
        console.log(message.data);
        const [messageType, data] = JSON.parse(message.data);

        if (messageType === 'Stdout') {
            const { stdout: dataStdout } = data;
            console.log(data);
            console.log(dataStdout);
            // @ts-ignore
          setStdout([...stdout, dataStdout])
        }
  }

  return (
  <React.Fragment>

    <TopToolbar>
      <Title headingLevel={"h2"}>Dashboard</Title>
    </TopToolbar>
	<Stack>
            <StackItem>
              <Card>
                <CardTitle>Standard Out</CardTitle>
                <CardBody>
                  {stdout.length !== 0 && (
                    <SimpleList style={{ whiteSpace: 'pre-wrap' }}>
                      {stdout.map((item, i) => (
                        <SimpleListItem key={i}><Ansi>{item}</Ansi></SimpleListItem>
                      ))}
                    </SimpleList>
                  )}
                </CardBody>
              </Card>
            </StackItem>
	</Stack>

  </React.Fragment>
)
}

export { Dashboard };
