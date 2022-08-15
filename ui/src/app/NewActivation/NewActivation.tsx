import {
  ActionGroup,
  Button,
  Card,
  CardBody as PFCardBody,
  Form,
  FormGroup,
  FormSelect,
  FormSelectOption,
  PageSection,
  SimpleList as PFSimpleList,
  Text,
  TextInput,
  TextVariants,
  Title,
  ValidatedOptions
} from '@patternfly/react-core';
import {Link, useHistory} from "react-router-dom";
import React, {useEffect, useState} from 'react';
import {getServer, postData} from '@app/utils/utils';
import styled from 'styled-components';
import {TopToolbar} from "@app/shared/top-toolbar";
import {ExclamationCircleIcon} from "@patternfly/react-icons";
import {useIntl} from "react-intl";
import sharedMessages from "../messages/shared.messages";

const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const endpoint = 'http://' + getServer() + '/api/activation_instance/';
const endpoint1 = 'http://' + getServer() + '/api/rule_set_files/';
const endpoint2 = 'http://' + getServer() + '/api/inventories/';
const endpoint3 = 'http://' + getServer() + '/api/extra_vars/';

const NewActivation: React.FunctionComponent = () => {
  const history = useHistory();
  const intl = useIntl();
  const [rules, setRules] = useState([{"id": 0, "name": "Please select a rule set"}])
  const [inventories, setInventories] = useState([{"id": 0, "name": "Please select an inventory"}]);
  const [extravars, setExtraVars] = useState([{"id": 0, "name": "Please select vars"}]);
  const [name, setName] = useState();
  const [ruleset, setRuleSet] = useState('');
  const [inventory, setInventory] = useState('');
  const [extravar, setExtraVar] = useState('');

  const [ validatedName, setValidatedName ] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [ validatedRuleSet, setValidatedRuleSet ] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [ validatedInventory, setValidatedInventory ] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [ validatedExtraVar, setValidatedExtraVar ] = useState<ValidatedOptions>(ValidatedOptions.default);
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

  const validateName = (value) => {
    (!value || value.length < 1 ) ?
      setValidatedName(ValidatedOptions.error) :
      setValidatedName(ValidatedOptions.default)
  }

  const onNameChange = (value) => {
    setName(value);
    validateName(value);
  };

  const validateRuleSet = (value) => {
    (!value || value.length < 1 ) ?
      setValidatedRuleSet(ValidatedOptions.error) :
      setValidatedRuleSet(ValidatedOptions.default)
  };

  const onRuleSetChange = (value) => {
    setRuleSet(value);
    validateRuleSet(value);
  };

  const validateInventory = (value) => {
    (!value || value.length < 1 ) ?
      setValidatedInventory(ValidatedOptions.error) :
      setValidatedInventory(ValidatedOptions.default)
  };

  const onInventoryChange = (value) => {
    setInventory(value);
    validateInventory(value);
  };

  const validateExtraVar = (value) => {
    (!value || value.length < 1 ) ?
      setValidatedExtraVar(ValidatedOptions.error) :
      setValidatedExtraVar(ValidatedOptions.default)
  }
  const onExtraVarChange = (value) => {
    setExtraVar(value);
    validateExtraVar(value);
  };

  const validateFields = () => {
    validateName(name);
    validateRuleSet(ruleset);
    validateInventory(inventory);
    validateExtraVar(extravar);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    validateFields();
    postData(endpoint, { name: name,
                         rule_set_file_id: ruleset,
                         inventory_id: inventory,
                         extra_var_id: extravar})
      .then(data => {
        console.log(data);
        data?.id ? history.push("/activation/" + data.id) :
          console.log('no activation was added')
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
          title: 'Rulebook activations',
          to: '/activations'
        }
      ]
      }>
      <Title headingLevel={"h2"}>Add new rulebook activation</Title>
    </TopToolbar>
    <PageSection>
      <Card>
        <CardBody>
          <Form>
            <Text component={TextVariants.small}>
              { intl.formatMessage(sharedMessages.allFieldsRequired) }
            </Text>
            <FormGroup label={intl.formatMessage(sharedMessages.name)}
                       fieldId={`activation-name`}
                       isRequired
                       helperTextInvalid={ intl.formatMessage(sharedMessages.enterRulebookActivationName) }
                       helperTextInvalidIcon={<ExclamationCircleIcon />}
                       validated={validatedName}
            >
              <TextInput
                id="activation-name"
                value={name}
                label="Name"
                isRequired
                validated={validatedName}
                onChange={onNameChange}
                onBlur={(event) => validateName(name)}
              />
            </FormGroup>
            <FormGroup label="Rule Set"
                       fieldId={`rule-set-${ruleset}`}
                       helperTextInvalid={ intl.formatMessage(sharedMessages.selectRuleSet) }
                       helperTextInvalidIcon={<ExclamationCircleIcon />}
                       validated={validatedRuleSet}>
              <FormSelect value={ruleset}
                          onChange={onRuleSetChange}
                          validated={validatedRuleSet}
                          onBlur={(event) => validateRuleSet(ruleset)}
                          aria-label="FormSelect Input RuleSet">
                {rules.map((option, index) => (
                  <FormSelectOption
                    key={index}
                    value={option.id}
                    label={"" + option.id + " "+ option.name} />
                ))}
              </FormSelect>
            </FormGroup>
            <FormGroup label="Inventory"
                       fieldId={'activation-name'}
                       helperTextInvalid={ intl.formatMessage(sharedMessages.selectInventory) }
                       helperTextInvalidIcon={<ExclamationCircleIcon />}
                       validated={validatedInventory}>
              <FormSelect value={inventory}
                          onChange={onInventoryChange}
                          onBlur={() => validateInventory(inventory)}
                          validated={validatedInventory}
                          aria-label="FormSelect Input Inventory">
                {inventories.map((option, index) => (
                  <FormSelectOption key={index} value={option.id}
                                    label={"" + option.id + " "+ option.name} />
                ))}
              </FormSelect>
            </FormGroup>
            <FormGroup label="Extra Vars"
                       fieldId={'activation-vars'}
                       helperTextInvalid={ intl.formatMessage(sharedMessages.selectExtraVar) }
                       helperTextInvalidIcon={<ExclamationCircleIcon />}
                       validated={validatedExtraVar}>
              <FormSelect value={extravar}
                          onChange={onExtraVarChange}
                          onBlur={() => validateExtraVar(extravar)}
                          validated={validatedExtraVar}
                          aria-label="FormSelect Input ExtraVar">
                {extravars.map((option, index) => (
                  <FormSelectOption key={index}
                                    value={option.id}
                                    label={"" + option.id + " "+ option.name} />
                ))}
              </FormSelect>
            </FormGroup>
            <ActionGroup>
              <Button variant="primary" onClick={handleSubmit}>Save</Button>
              <Button variant="link" onClick={() => history.push('/activations')}> Cancel</Button>
            </ActionGroup>
          </Form>
        </CardBody>
      </Card>
    </PageSection>
  </React.Fragment>
)
}

export { NewActivation };
