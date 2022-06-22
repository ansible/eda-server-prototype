import * as React from 'react';
import { PageSection, Title } from '@patternfly/react-core';
import { useDispatch } from 'react-redux';
import { Link } from 'react-router-dom';
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
import styled from 'styled-components';
import {getServer} from '@app/utils/utils';


const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`

const endpoint = 'http://' + getServer() + '/api/rulesetfiles/';

const RuleSetFiles: React.FunctionComponent = () => {


  const [rulesetfiles, setRuleSetFiles] = useState([]);

  useEffect(() => {
     fetch(endpoint, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setRuleSetFiles(data));
  }, []);

  return (
  <React.Fragment>
  <PageSection>
    <Title headingLevel="h1" size="lg">Event Driven Automation | Rule Set Files</Title>
  </PageSection>

	<Stack>
            <StackItem>
              <Card>
                <CardTitle>Rule Sets</CardTitle>
                <CardBody>
                  {rulesetfiles.length !== 0 && (
                    <SimpleList style={{ whiteSpace: 'pre-wrap' }}>
                      {rulesetfiles.map((item, i) => (
                        <SimpleListItem key={i}><Link to={"/rulesetfile/" + item.id}>{item.name} </Link></SimpleListItem>
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

export { RuleSetFiles };
