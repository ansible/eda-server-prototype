import * as React from 'react';
import { PageSection, Title } from '@patternfly/react-core';
import { useDispatch } from 'react-redux';
import { Link, useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import { CodeBlock, CodeBlockCode  } from '@patternfly/react-core';

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

const endpoint = 'http://' + getServer() + '/api/rulesetfile/';
const endpoint2 = 'http://' + getServer() + '/api/rulesetfile_json/';

const RuleSetFile: React.FunctionComponent = () => {

  const [rulesetfile, setRuleSetFile] = useState([]);
  const [rulesets, setRuleSets] = useState([]);

  let { id } = useParams();
  console.log(id);

  useEffect(() => {
     fetch(endpoint + id, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setRuleSetFile(data));
     fetch(endpoint2 + id, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setRuleSets(data.rulesets));
  }, []);

  return (
  <React.Fragment>
  <PageSection>
    <Title headingLevel="h1" size="lg">Event Driven Automation | Rule Set {rulesetfile.name}</Title>
  </PageSection>

	<Stack>

            <StackItem>
              <Card>
                <CardTitle>Rule Sets</CardTitle>
                <CardBody>
                  {rulesets.length !== 0 && (
                    <SimpleList style={{ whiteSpace: 'pre-wrap' }}>
                      {rulesets.map((item, i) => (
                        <SimpleListItem>{item.name}
                        <div>
                        { item.sources.map((source, j) => (
                        <div> {source.name} </div>))}
                        { item.rules.map((rule, j) => (
                        <div> {rule.name} {Object.keys(rule.action)} </div>))}
                        </div>
                        </SimpleListItem>
                      )) }
                    </SimpleList>
                  )}
                </CardBody>
              </Card>
            </StackItem>
            <StackItem>
              <Card>
    <CodeBlock>
      <CodeBlockCode id="code-content">{rulesetfile.rulesets}</CodeBlockCode>
    </CodeBlock>
              </Card>
            </StackItem>
	</Stack>
  </React.Fragment>
)
}

export { RuleSetFile };
