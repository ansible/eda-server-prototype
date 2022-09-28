import React, { useState, useEffect } from 'react';
import { Title } from '@patternfly/react-core';
import { useParams } from 'react-router-dom';
import { CodeBlock, CodeBlockCode  } from '@patternfly/react-core';

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
import {RuleSetType} from "@app/RuleSetFiles/RuleSetFiles";


const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`

const endpoint = 'http://' + getServer() + '/api/rulebooks/';
const endpoint2 = 'http://' + getServer() + '/api/rulebook_json/';

const RuleSetFile: React.FunctionComponent = () => {

  const [ruleSetFile, setRuleSetFile] = useState<RuleSetType|undefined>(undefined);
  const [rulesets, setRuleSets] = useState<RuleSetType[]>([]);

  const { id } = useParams<{id:string}>();
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
    <TopToolbar>
      <Title headingLevel={"h2"}>{`Rule set ${ruleSetFile?.name}`}</Title>
    </TopToolbar>
    <Stack>
      <StackItem>
          <Card>
            <CardTitle>Rule Sets</CardTitle>
            <CardBody>
              {rulesets && rulesets.length !== 0 && (
                <SimpleList style={{ whiteSpace: 'pre-wrap' }}>
                  {rulesets.map((item, i) => (
                    <SimpleListItem key={`ruleset-${item?.name}`}>{item?.name}
                      <div>
                        { item?.sources && item.sources.length > 0 && item.sources.map((source, j) => (
                          <div key={`source-${source?.id}`}> {source.name} </div>))}
                        { item?.rules && item.rules.length > 0 && item.rules.map((rule, j) => (
                          <div key={`rule-${rule?.id}`}> {rule?.name} {rule?.action ? Object.keys(rule?.action) : ''} </div>))}
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
      <CodeBlockCode id="code-content">{ruleSetFile?.rulesets}</CodeBlockCode>
    </CodeBlock>
              </Card>
            </StackItem>
	</Stack>
  </React.Fragment>
)
}

export { RuleSetFile };
