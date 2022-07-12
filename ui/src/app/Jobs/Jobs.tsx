import { PageSection, Title } from '@patternfly/react-core';
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
import {getServer} from '@app/utils/utils';
import {TopToolbar} from "@app/shared/top-toolbar";


const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`

const endpoint = 'http://' + getServer() + '/api/job_instances/';

const Jobs: React.FunctionComponent = () => {

  const [jobs, setJobs] = useState([]);

  useEffect(() => {
     fetch(endpoint, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setJobs(data));
  }, []);

  return (
  <React.Fragment>
    <TopToolbar>
      <Title headingLevel={"h2"}>Jobs</Title>
    </TopToolbar>
    <Stack>
      <StackItem>
        <Card>
          <CardTitle>Jobs</CardTitle>
          <CardBody>
            {jobs.length !== 0 && (
              <SimpleList style={{ whiteSpace: 'pre-wrap' }}>
                {jobs.map((item, i) => (
                  <SimpleListItem key={i}><Link to={"/job/" + item.id}>{item.id} </Link></SimpleListItem>
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

export { Jobs };
