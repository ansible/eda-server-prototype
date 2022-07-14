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
import {TopToolbar} from "@app/shared/top-toolbar";

const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`

const endpoint = 'http://' + getServer() + '/api/rule_set_files/';

const RuleSetFiles: React.FunctionComponent = () => {


  const [ruleSetFiles, setRuleSetFiles] = useState([]);

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
    <TopToolbar>
      <Title headingLevel={"h2"}>Rule set files</Title>
    </TopToolbar>
    <Stack>
      <StackItem>
        <Card>
          <CardTitle>Rule Sets</CardTitle>
          <CardBody>
            {ruleSetFiles.length !== 0 && (
              <SimpleList style={{ whiteSpace: 'pre-wrap' }}>
                {ruleSetFiles.map((item, i) => (
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
