import { PageSection, Title } from '@patternfly/react-core';
import { useHistory } from "react-router-dom";
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
import { ActionGroup, Button, Form, FormGroup, TextInput } from '@patternfly/react-core';
import { FormSelect, FormSelectOption, FormSelectOptionGroup } from '@patternfly/react-core';
import { postData } from '@app/utils/utils';
import {getServer} from '@app/utils/utils';

import styled from 'styled-components';
import {TopToolbar} from "@app/shared/top-toolbar";


const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`

const endpoint = 'http://' + getServer() + '/api/activation_instance/';
const endpoint1 = 'http://' + getServer() + '/api/rule_set_files/';
const endpoint2 = 'http://' + getServer() + '/api/inventories/';
const endpoint3 = 'http://' + getServer() + '/api/extra_vars/';

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
                           rule_set_file_id: ruleset,
                           inventory_id: inventory,
                           extra_var_id: extravar})
				.then(data => {
					console.log(data);
          history.push(`/activation/${data.id}/details`);
			});
  };

  console.log(rules);
  console.log(inventories);
  console.log(extravars);

  return (
  <React.Fragment>
    <TopToolbar
      breadcrumbs={[
        {
          title: 'Activations',
          to: '/activations'
        }
      ]
      }>
      <Title headingLevel={"h2"}>New activation</Title>
    </TopToolbar>
    <PageSection>
      <Card>
        <CardBody>
          <Form>
            <FormGroup label="Name"  fieldId={`activation-name`}>
              <TextInput
                id="activation-name"
                onChange={setName}
                value={name}
              />
          </FormGroup>
            <FormGroup label="Rule Set"  fieldId={`rule-set-${ruleset}`}>
              <FormSelect value={ruleset} onChange={setRuleSet} aria-label="FormSelect Input">
            {rules.map((option, index) => (
              <FormSelectOption key={index} value={option.id} label={"" + option.id + " "+ option.name} />
            ))}
          </FormSelect>
            </FormGroup>
            <FormGroup label="Inventory" fieldId={'activation-name'}>
              <FormSelect value={inventory} onChange={setInventory} aria-label="FormSelect Input2">
            {inventories.map((option, index) => (
              <FormSelectOption key={index} value={option.id} label={"" + option.id + " "+ option.name} />
            ))}
          </FormSelect>
            </FormGroup>
            <FormGroup label="Extra Vars" fieldId={'activation-vars'}>
              <FormSelect value={extravar} onChange={setExtraVar} aria-label="FormSelect Input3">
            {extravars.map((option, index) => (
              <FormSelectOption key={index} value={option.id} label={"" + option.id + " "+ option.name} />
            ))}
          </FormSelect>
            </FormGroup>
            <ActionGroup>
              <Button variant="primary" onClick={handleSubmit}>Save</Button>
              <Button variant="link">Cancel</Button>
            </ActionGroup>
          </Form>
        </CardBody>
      </Card>
    </PageSection>
  </React.Fragment>
)
}

export { NewActivation };
