import * as React from 'react';
import { PageSection, Title } from '@patternfly/react-core';
import { useDispatch } from 'react-redux';
import { useHistory } from "react-router-dom";
import { Link, useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
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
import { ActionGroup, Button, Form, FormGroup, TextInput } from '@patternfly/react-core';
import { postData } from '@app/utils/utils';

import styled from 'styled-components';


const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`

const endpoint = 'http://' + window.location.hostname  + ':' + process.env.SERVER_PORT + '/project/';

const NewProject: React.FunctionComponent = () => {

  const history = useHistory();

  const [value, setValue] = useState('');

  const handleSubmit = () => {
      console.log('submit ' + value);
			postData(endpoint, { url: value })
				.then(data => {
					console.log(data);
          history.push("/project/" + data.id);
			});
  };

  return (
  <React.Fragment>
  <PageSection>
    <Title headingLevel="h1" size="lg">Event Driven Automation | New Project</Title>
  </PageSection>
     <Form>
        <FormGroup
          label="Git URL"
          fieldId="url-1"
        >
          <TextInput
            onChange={setValue}
            value={value}
            id="url-1"
          />
        </FormGroup>
        <ActionGroup>
          <Button variant="primary" onClick={handleSubmit}>Submit</Button>
          <Button variant="link">Cancel</Button>
        </ActionGroup>
      </Form>
  </React.Fragment>
)
}

export { NewProject };
