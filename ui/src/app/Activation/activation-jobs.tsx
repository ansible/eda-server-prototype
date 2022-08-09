import {CardBody, PageSection, SimpleList} from '@patternfly/react-core';
import { Link } from 'react-router-dom';
import React from 'react';
import {
  Card,
  CardTitle,
  SimpleListItem,
  Stack,
  StackItem
} from '@patternfly/react-core';
import {renderActivationTabs} from "@app/Activation/Activation";
import {ActivationType} from "@app/Activations/Activations";
import {JobType} from "@app/Job/Job";

const ActivationJobs: React.FunctionComponent<{activation: ActivationType, jobs: JobType[]}> = ({activation, jobs}) => {

  return (
    <PageSection page-type={'activation-details'} id={'activation-details'}>
      { renderActivationTabs(activation?.id) }
      <Stack>
        <StackItem>
          <Card>
            <CardTitle>Jobs</CardTitle>
            <CardBody>
              {jobs.length !== 0 && (
                <SimpleList style={{whiteSpace: 'pre-wrap'}}>
                  {jobs.map((item, i) => (
                    <SimpleListItem key={i}><Link to={"/job/" + item.id}>{item.id} </Link></SimpleListItem>
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

export { ActivationJobs };
