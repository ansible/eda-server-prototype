import {CardBody, PageSection, SimpleList} from '@patternfly/react-core';
import React from 'react';
import {
  Card,
  CardTitle,
  SimpleListItem,
  Stack,
  StackItem,
} from '@patternfly/react-core';
import {renderActivationTabs} from "@app/Activation/Activation";
import Ansi from "ansi-to-react";
import {ActivationType} from "@app/Activations/Activations";
import {StdoutType} from "@app/Job/Job";

const ActivationStdout: React.FunctionComponent<{activation: ActivationType, stdout: StdoutType[]}> = ({activation, stdout}) => {
  return (
    <PageSection page-type={'activation-details'} id={'activation-details'}>
      { renderActivationTabs(activation.id) }
      <Stack>
        <StackItem>
          <Card>
            <CardTitle>Standard Out</CardTitle>
            <CardBody>
              {stdout && stdout.length > 0 && (
                <SimpleList style={{ whiteSpace: 'pre-wrap' }}>
                  {stdout.map((item, i) => (
                    <SimpleListItem key={i}><Ansi>{item?.stdout}</Ansi></SimpleListItem>
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
