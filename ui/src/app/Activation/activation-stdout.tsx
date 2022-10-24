import {CardBody, PageSection, SimpleList} from '@patternfly/react-core';
import React, { useState, useEffect } from 'react';
import {
  Card,
  CardTitle,
  SimpleListItem,
  Stack,
  StackItem,
} from '@patternfly/react-core';
import {useIntl} from "react-intl";
import {getServer} from "@app/utils/utils";
import {renderActivationTabs} from "@app/Activation/Activation";
import Ansi from "ansi-to-react";
import {ActivationType} from "@app/Activations/Activations";
import {fetchActivationOutput} from "@app/API/Activation";

const ActivationStdout: React.FunctionComponent<{activation: ActivationType}> = ({activation}) => {
  const intl = useIntl();
  const [stdout, setStdout] = useState<string[]>([]);
  const [newStdout, setNewStdout] = useState<string>('');

  useEffect(() => {
    fetchActivationOutput(activation.id)
  }, []);

  const [update_client, setUpdateClient] = useState<WebSocket|unknown>({});
  useEffect(() => {
    const uc = new WebSocket('ws://' + getServer() + '/api/ws-activation/' + activation.id);
    setUpdateClient(uc);
    uc.onopen = () => {
      console.log('Update client connected');
    };
    uc.onmessage = (message) => {
      const [messageType, data] = JSON.parse(message.data);
      if (messageType === 'Stdout') {
        const { stdout: dataStdout } = data;
        setNewStdout(dataStdout);
      }
    }
  }, []);

  useEffect(() => {
    setStdout([...stdout, newStdout]);
  }, [newStdout]);

  return (
    <PageSection page-type={'activation-details'} id={'activation-details'}>
      { renderActivationTabs(activation.id, intl) }
      <Stack>
        <StackItem>
          <Card>
            <CardTitle>Standard Out</CardTitle>
            <CardBody>
              {stdout && stdout.length > 0 && (
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
    </PageSection>
  );
}

export { ActivationStdout };
