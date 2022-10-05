import {
  ActionGroup,
  Button,
  Card,
  CardBody as PFCardBody,
  Form,
  FormGroup,
  FormSelect,
  FormSelectOption, Grid, GridItem,
  PageSection,
  TextInput,
  Title,
  ValidatedOptions
} from '@patternfly/react-core';
import {useHistory} from "react-router-dom";
import React, {useEffect, useState} from 'react';
import {getServer, postData} from '@app/utils/utils';
import styled from 'styled-components';
import {TopToolbar} from "@app/shared/top-toolbar";
import {ExclamationCircleIcon} from "@patternfly/react-icons";
import {useIntl} from "react-intl";
import sharedMessages from "../messages/shared.messages";
import {ExtraVarType} from "@app/Vars/Vars";
import {InventoryType, RuleType} from "@app/RuleSets/RuleSets";

const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const endpoint_activation = 'http://' + getServer() + '/api/activations/';
const endpoint_rulebooks = 'http://' + getServer() + '/api/rulebooks/';
const endpoint_inventories = 'http://' + getServer() + '/api/inventories/';
const endpoint_vars = 'http://' + getServer() + '/api/extra_vars/';

export interface ExecutionEnvironmentType {
  id: string;
  name?: string;
}

export interface RestartPolicyType {
  id: string;
  name?: string;
}

const NewActivation: React.FunctionComponent = () => {
  const history = useHistory();
  const intl = useIntl();
  const [rulebooks, setRuleBooks] = useState<RuleType[]>([{id:'', name:intl.formatMessage(sharedMessages.ruleBookPlaceholder)}]);
  const [inventories, setInventories] = useState<InventoryType[]>([{id:'', name: intl.formatMessage(sharedMessages.inventoryPlaceholder) }]);
  const [extravars, setExtraVars] = useState<ExtraVarType[]>([{id:'', name:intl.formatMessage(sharedMessages.extraVarPlaceholder), extra_var:''}]);
  const [executionEnvironments, setExecutionEnvironments] = useState<ExecutionEnvironmentType[]>([{id:'',
    name:intl.formatMessage(sharedMessages.executionEnvironmentPlaceholder)}]);
  const [restartPolicies, setRestartPolicies] = useState<RestartPolicyType[]>([{id:'', name: intl.formatMessage(sharedMessages.restartPolicyPlaceholder)}]);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [executionEnvironment, setExecutionEnvironment] = useState('');
  const [restartPolicy, setRestartPolicy] = useState('');
  const [rulebook, setRuleBook] = useState('');
  const [inventory, setInventory] = useState('');
  const [extravar, setExtraVar] = useState('');
  const [workingDirectory, setWorkingDirectory] = useState('');

  const [ validatedName, setValidatedName ] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [ validatedRuleBook, setValidatedRuleBook ] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [ validatedInventory, setValidatedInventory ] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [ validatedExtraVar, setValidatedExtraVar ] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [ validatedWorkingDirectory, setValidatedWorkingDirectory ] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [ validatedExecutionEnvironment, setValidatedExecutionEnvironment ] = useState<ValidatedOptions>(ValidatedOptions.default);

  useEffect(() => {
     fetch(endpoint_rulebooks, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setRuleBooks([...rulebooks, ...data]));
  }, []);

  useEffect(() => {
     fetch(endpoint_inventories, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setInventories([...inventories, ...data]));
  }, []);

  useEffect(() => {
     fetch(endpoint_vars, {
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

  const onDescriptionChange = (value) => {
    setDescription(value);
  };

  const onExecutionEnvironmentChange = (value) => {
    setExecutionEnvironment(value);
    validateExecutionEnvironment(value);
  };

  const onRestartPolicyChange = (value) => {
    setRestartPolicy(value);
  };

  const validateRuleBook = (value) => {
    (!value || value.length < 1 ) ?
      setValidatedRuleBook(ValidatedOptions.error) :
      setValidatedRuleBook(ValidatedOptions.default)
  };

  const onRuleBookChange = (value) => {
    setRuleBook(value);
    validateRuleBook(value);
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

  const validateExecutionEnvironment = (value) => {
    setValidatedExecutionEnvironment(ValidatedOptions.default)
  }

  const validateWorkingDirectory = (value) => {
    setValidatedWorkingDirectory(ValidatedOptions.default)
  }

  const onWorkingDirectoryChange = (value) => {
    setWorkingDirectory(value);
    validateWorkingDirectory(value);
  };

  const validateFields = () => {
    validateName(name);
    validateRuleBook(rulebook);
    validateInventory(inventory);
    validateExtraVar(extravar);
    validateWorkingDirectory(workingDirectory);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    validateFields();
    postData(endpoint_activation, {
      name: name,
      description: description,
      status: '',
      rulebook_id: rulebook,
      inventory_id: inventory,
      restart_policy: restartPolicy || "on-failure",
      is_enabled: true,
      extra_var_id: extravar,
      working_directory: workingDirectory,
      execution_environment: executionEnvironment || 'docker'})
      .then(() => history.push("/activations"))
      .catch(() => history.push("/activations"));
    }

  return (
  <React.Fragment>
    <TopToolbar
      breadcrumbs={[
        {
          title: 'Rulebook Activations',
          to: '/activations'
        },
        {
          title: 'Add'
        }
      ]
      }>
      <Title headingLevel={"h2"}>Add new rulebook activation</Title>
    </TopToolbar>
    <PageSection>
      <Card>
        <CardBody>
          <Form>
            <Grid hasGutter>
              <GridItem span={4}>
                <FormGroup style={{paddingRight: '30px'}}
                           label={intl.formatMessage(sharedMessages.name)}
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
                    placeholder={ intl.formatMessage(sharedMessages.namePlaceholder) }
                  />
                </FormGroup>
              </GridItem>
              <GridItem span={4}>
                <FormGroup style={{paddingRight: '30px'}}
                           label={intl.formatMessage(sharedMessages.description)}
                           fieldId={`activation-description`}
                           helperTextInvalid={ intl.formatMessage(sharedMessages.enterRulebookActivationDescription) }
                           helperTextInvalidIcon={<ExclamationCircleIcon />}
                >
                  <TextInput
                    id="activation-description"
                    label="Description"
                    placeholder={ intl.formatMessage(sharedMessages.descriptionPlaceholder) }
                    onChange={onDescriptionChange}
                  />
                </FormGroup>
              </GridItem>
              <GridItem span={4}>
                <FormGroup style={{paddingRight: '30px'}}
                           label="Inventory"
                           fieldId={'activation-inventory'}
                           helperTextInvalid={ intl.formatMessage(sharedMessages.selectInventory) }
                           helperTextInvalidIcon={<ExclamationCircleIcon />}
                           validated={validatedInventory}>
                  <FormSelect value={inventory}
                              placeholder={ intl.formatMessage(sharedMessages.inventoryPlaceholder) }
                              onChange={onInventoryChange}
                              onBlur={() => validateInventory(inventory)}
                              validated={validatedInventory}
                              aria-label="FormSelect Input Inventory">
                    {inventories.map((option, index) => (
                      <FormSelectOption key={index} value={option?.id}
                                        label={`${option?.id} ${option?.name}`}
                                        isPlaceholder={option?.id===''}/>
                    ))}
                  </FormSelect>
                </FormGroup>
              </GridItem>
              <GridItem span={4}>
                <FormGroup style={{paddingRight: '30px'}}
                           label="Execution environment"
                           fieldId={'activation-exec-env'}
                           helperTextInvalid={ intl.formatMessage(sharedMessages.selectExecutionEnvironment) }
                           helperTextInvalidIcon={<ExclamationCircleIcon />}>
                  <TextInput
                    id="activation-exec-env"
                    value={executionEnvironment}
                    label="Execution environment"
                    validated={validatedExecutionEnvironment}
                    onChange={onExecutionEnvironmentChange}
                    onBlur={(event) => validateExecutionEnvironment(executionEnvironment)}
                    placeholder={ intl.formatMessage(sharedMessages.executionEnvironmentPlaceholder) }
                  />
                </FormGroup>
              </GridItem>
              <GridItem span={4}>
                <FormGroup style={{paddingRight: '30px'}}  label="Restart policy"
                           fieldId={'activation-restart-policy'}
                           helperTextInvalid={ intl.formatMessage(sharedMessages.selectRestartPolicy) }
                           helperTextInvalidIcon={<ExclamationCircleIcon />}>
                  <FormSelect value={restartPolicy}
                              placeholder={ intl.formatMessage(sharedMessages.restartPolicyPlaceholder) }
                              onChange={onRestartPolicyChange}
                              aria-label="FormSelect Input Restart Policy">
                    {restartPolicies.map((option, index) => (
                      <FormSelectOption key={index} value={option?.id}
                                        label={`${option?.id} ${option?.name}`}
                                        isPlaceholder={option?.id===''}/>
                    ))}
                  </FormSelect>
                </FormGroup>
              </GridItem>
              <GridItem span={4}>
                <FormGroup style={{paddingRight: '30px'}}  label="Rulebook"
                           fieldId={`rule-set-${rulebook}`}
                           helperTextInvalid={ intl.formatMessage(sharedMessages.selectRuleBook) }
                           helperTextInvalidIcon={<ExclamationCircleIcon />}
                           validated={validatedRuleBook}>
                  <FormSelect value={rulebook}
                              onChange={onRuleBookChange}
                              validated={validatedRuleBook}
                              placeholder={ intl.formatMessage(sharedMessages.ruleBookPlaceholder) }
                              onBlur={(event) => validateRuleBook(rulebook)}
                              aria-label="FormSelect Input Rulebook">
                    {rulebooks.map((option, index) => (
                      <FormSelectOption
                        key={index}
                        value={option?.id}
                        label={`${option?.id} ${option?.name}`}
                        isPlaceholder={option?.id===''}/>
                    ))}
                  </FormSelect>
                </FormGroup>
              </GridItem>
              <GridItem span={4}>
                <FormGroup style={{paddingRight: '30px'}}  label="Extra Vars"
                           fieldId={'activation-vars'}
                           helperTextInvalid={ intl.formatMessage(sharedMessages.selectExtraVar) }
                           helperTextInvalidIcon={<ExclamationCircleIcon />}
                           validated={validatedExtraVar}>
                  <FormSelect value={extravar}
                              onChange={onExtraVarChange}
                              placeholder={ intl.formatMessage(sharedMessages.extraVarPlaceholder) }
                              onBlur={() => validateExtraVar(extravar)}
                              validated={validatedExtraVar}
                              aria-label="FormSelect Input ExtraVar">
                    {extravars.map((option, index) => (
                      <FormSelectOption key={index}
                                        value={option?.id}
                                        label={`${option?.id} ${option?.name}`}
                                        isPlaceholder={option?.id===''}/>
                    ))}
                  </FormSelect>
                </FormGroup>
              </GridItem>

              <GridItem span={4}>
                <FormGroup style={{paddingRight: '30px'}}
                           label={intl.formatMessage(sharedMessages.workingDirectory)}
                           fieldId={`activation-working-directory`}
                           helperTextInvalid={ intl.formatMessage(sharedMessages.enterRulebookActivationWorkingDirectory) }
                           helperTextInvalidIcon={<ExclamationCircleIcon />}
                           validated={validatedWorkingDirectory}
                >
                  <TextInput
                    id="activation-working-directory"
                    value={workingDirectory}
                    label="WorkingDirectory"
                    isRequired
                    validated={validatedWorkingDirectory}
                    onChange={onWorkingDirectoryChange}
                    onBlur={(event) => validateWorkingDirectory(workingDirectory)}
                    placeholder={ intl.formatMessage(sharedMessages.workingDirectoryPlaceholder) }
                  />
                </FormGroup>
              </GridItem>

            </Grid>
            <ActionGroup>
              <Button variant="primary" onClick={handleSubmit}>Add</Button>
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
