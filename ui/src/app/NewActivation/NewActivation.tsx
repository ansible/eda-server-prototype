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
import { FormSelect, FormSelectOption, FormSelectOptionGroup } from '@patternfly/react-core';
import { postData } from '@app/utils/utils';
import {getServer} from '@app/utils/utils';

import styled from 'styled-components';


const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`

const endpoint = 'http://' + getServer() + '/api/activation/';
const endpoint1 = 'http://' + getServer() + '/api/rulesetfiles/';
const endpoint2 = 'http://' + getServer() + '/api/inventories/';
const endpoint3 = 'http://' + getServer() + '/api/extravars/';

const NewActivation: React.FunctionComponent = () => {

  const history = useHistory();

  const [rules, setRules] = useState([{"id": 0, "name": "Please select a rule set"}])
  const [inventories, setInventories] = useState([{"id": 0, "name": "Please select an inventory"}]);
  const [extravars, setExtraVars] = useState([{"id": 0, "name": "Please select vars"}]);

  useEffect(() => {
     fetch(endpoint1, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setRules([...rules, ...data]));
  }, []);

  useEffect(() => {
     fetch(endpoint2, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setInventories([...inventories, ...data]));
  }, []);

  useEffect(() => {
     fetch(endpoint3, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setExtraVars([...extravars, ...data]));
  }, []);

  const [name, setName] = useState('');
  const [ruleset, setRuleSet] = useState('');
  const [inventory, setInventory] = useState('');
  const [extravar, setExtraVar] = useState('');

  const handleSubmit = () => {
			postData(endpoint, { name: name,
                           rulesetfile_id: ruleset,
                           inventory_id: inventory,
                           extravars_id: extravar})
				.then(data => {
					console.log(data);
          history.push("/activation/" + data.id);
			});
  };

  console.log(rules);
  console.log(inventories);
  console.log(extravars);

  return (
  <React.Fragment>
  <PageSection>
    <Title headingLevel="h1" size="lg">Event Driven Automation | New Project</Title>
  </PageSection>
     <Form>
        <FormGroup label="Name" >
          <TextInput
            id="activation-name"
            onChange={setName}
            value={name}
          />
        </FormGroup>
        <FormGroup label="Rule Set" >
          <FormSelect value={ruleset} onChange={setRuleSet} aria-label="FormSelect Input">
        {rules.map((option, index) => (
          <FormSelectOption key={index} value={option.id} label={"" + option.id + " "+ option.name} />
        ))}
      </FormSelect>
        </FormGroup>
        <FormGroup label="Inventory" >
          <FormSelect value={inventory} onChange={setInventory} aria-label="FormSelect Input2">
        {inventories.map((option, index) => (
          <FormSelectOption key={index} value={option.id} label={"" + option.id + " "+ option.name} />
        ))}
      </FormSelect>
        </FormGroup>
        <FormGroup label="Extra Vars" >
          <FormSelect value={extravar} onChange={setExtraVar} aria-label="FormSelect Input3">
        {extravars.map((option, index) => (
          <FormSelectOption key={index} value={option.id} label={"" + option.id + " "+ option.name} />
        ))}
      </FormSelect>
        </FormGroup>
        <ActionGroup>
          <Button variant="primary" onClick={handleSubmit}>Submit</Button>
          <Button variant="link">Cancel</Button>
        </ActionGroup>
      </Form>
  </React.Fragment>
)
}

export { NewActivation };
