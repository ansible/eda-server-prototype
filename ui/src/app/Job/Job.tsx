import {
  Dropdown,
  DropdownItem,
  DropdownPosition,
  KebabToggle,
  Level,
  LevelItem,
  PageSection,
  Title
} from '@patternfly/react-core';
import {Link, Route, useParams} from 'react-router-dom';
import React, {useState, useEffect, Fragment} from 'react';
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
import sharedMessages from "../messages/shared.messages";
import {AnyObject} from "@app/shared/types/common-types";
import {RemoveProject} from "@app/RemoveProject/RemoveProject";
import {useIntl} from "react-intl";
import {RemoveJob} from "@app/RemoveJob/RemoveJob";

export interface JobType {
  id: string;
  name: string;
}

const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`

const endpoint = 'http://' + getServer() + '/api/job_instance/';
const event_endpoint = 'http://' + getServer() + '/api/job_instance_events/';

const Job: React.FunctionComponent = () => {

  const [job, setJob] = useState<JobType|undefined>(undefined);
  const [stdout, setStdout] = useState<any[]>([]);
  const [newStdout, setNewStdout] = useState<string>('');
  const [update_client, setUpdateClient] = useState<WebSocket|unknown>({});
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
    }
  }, []);

  useEffect(() => {
    setStdout([...stdout, newStdout]);
  }, [newStdout]);

  useEffect(() => {
     fetch(endpoint + id, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setJob(data));
     fetch(event_endpoint + id, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setStdout(data));
  }, []);

  const dropdownItems = [
    <DropdownItem
      aria-label="Edit"
      key="edit-job"
      id="edit-job"
      component={ <Link to={`/edit-job/${id}`}>
        {intl.formatMessage(sharedMessages.edit)}
      </Link>
      }
      role="link"
    />,
    <DropdownItem
      aria-label="Launch"
      key="launch-job"
      id="launch-job"
      component={ <Link to={`/job/${id}/launch`}>
        {intl.formatMessage(sharedMessages.launch)}
      </Link>
      }
      role="link"
    />,
    <DropdownItem
      aria-label="Delete"
      key="delete-job"
      id="delete-job"
      component={ <Link to={`/job/${id}/remove`}>
        {intl.formatMessage(sharedMessages.delete)}
      </Link>
      }
      role="link"
    />
  ]

  const routes = () => <Fragment>
    <Route exact path="/job/:id/remove"
           render={ (props: AnyObject) => <RemoveJob {...props}/> }/>
  </Fragment>;

  return (
  <React.Fragment>
    { routes() }
    <TopToolbar>
      <Level>
        <LevelItem>
          <Title headingLevel={"h2"}>{ job?.name || `Job ${job?.id}` }</Title>
        </LevelItem>
        <LevelItem>
          <Dropdown
            isPlain
            onSelect={() => setOpen(false)}
            position={DropdownPosition.right}
            toggle={
              <KebabToggle
                id="job-details-toggle"
                onToggle={(isOpen) => setOpen(isOpen)}
              />}
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
          <CardBody>
            {stdout.length !== 0 && (
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
  </React.Fragment>
)
}

export { Job };
