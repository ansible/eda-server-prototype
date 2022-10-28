import { Dropdown, DropdownItem, DropdownPosition, KebabToggle, Level, LevelItem, Title } from '@patternfly/react-core';
import { Link, Route, useParams } from 'react-router-dom';
import React, { useState, useEffect, Fragment } from 'react';
import { Card, CardBody as PFCardBody, CardTitle, Stack, StackItem } from '@patternfly/react-core';
import styled from 'styled-components';
import { getServer } from '@app/utils/utils';
import { TopToolbar } from '@app/shared/top-toolbar';
import sharedMessages from '../messages/shared.messages';
import { AnyObject } from '@app/shared/types/common-types';
import { useIntl } from 'react-intl';
import { RemoveJob } from '@app/RemoveJob/RemoveJob';
import { fetchJob, fetchJobEvents } from '@app/API/Job';
import { LogViewer } from '@patternfly/react-log-viewer';

export interface JobType {
  id: string;
  name: string;
}

const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
`;
const Job: React.FunctionComponent = () => {
  const [job, setJob] = useState<JobType | undefined>(undefined);
  const [stdout, setStdout] = useState<any[]>([]);
  const [newStdout, setNewStdout] = useState<string>('');
  const [update_client, setUpdateClient] = useState<WebSocket | unknown>({});
  const [isOpen, setOpen] = useState<boolean>(false);

  const { id } = useParams<JobType>();
  const intl = useIntl();

  useEffect(() => {
    const uc = new WebSocket('ws://' + getServer() + '/api/ws-job/' + id);
    setUpdateClient(uc);
    uc.onopen = () => {
      console.log('Update client connected');
    };
    uc.onmessage = (message) => {
      console.log('update: ' + message.data);
      const [messageType, data] = JSON.parse(message.data);
      if (messageType === 'Stdout') {
        setNewStdout(data);
      }
    };
  }, []);

  useEffect(() => {
    setStdout([...stdout, newStdout]);
  }, [newStdout]);

  useEffect(() => {
    fetchJob(id).then((data) => setJob(data.data));
    fetchJobEvents(id).then((data) => setStdout(data.data));
  }, []);

  const dropdownItems = [
    <DropdownItem
      aria-label="Edit"
      key="edit-job"
      id="edit-job"
      component={<Link to={`/job/${id}/edit`}>{intl.formatMessage(sharedMessages.edit)}</Link>}
      role="link"
    />,
    <DropdownItem
      aria-label="Launch"
      key="launch-job"
      id="launch-job"
      component={<Link to={`/job/${id}/launch`}>{intl.formatMessage(sharedMessages.launch)}</Link>}
      role="link"
    />,
    <DropdownItem
      aria-label="Delete"
      key="delete-job"
      id="delete-job"
      component={<Link to={`/job/${id}/remove`}>{intl.formatMessage(sharedMessages.delete)}</Link>}
      role="link"
    />,
  ];

  const routes = () => (
    <Fragment>
      <Route exact path="/job/:id/remove" render={(props: AnyObject) => <RemoveJob {...props} />} />
    </Fragment>
  );
  const logStdout = stdout && stdout.length > 0 ? stdout.map(({ stdout }) => stdout) : [];
  return (
    <React.Fragment>
      {routes()}
      <TopToolbar>
        <Level>
          <LevelItem>
            <Title headingLevel={'h2'}>{job?.name || `Job ${job?.id}`}</Title>
          </LevelItem>
          <LevelItem>
            <Dropdown
              isPlain
              onSelect={() => setOpen(false)}
              position={DropdownPosition.right}
              toggle={<KebabToggle id="job-details-toggle" onToggle={(isOpen) => setOpen(isOpen)} />}
              isOpen={isOpen}
              dropdownItems={dropdownItems}
            />
          </LevelItem>
        </Level>
      </TopToolbar>
      <Stack>
        <StackItem>
          <Card>
            <CardTitle>Standard Out</CardTitle>
            <CardBody>{stdout && stdout.length > 0 && <LogViewer hasLineNumbers={false} data={logStdout} />}</CardBody>
          </Card>
        </StackItem>
      </Stack>
    </React.Fragment>
  );
};

export { Job };
