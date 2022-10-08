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
import {addNotification} from '@redhat-cloud-services/frontend-components-notifications';
import {useDispatch} from "react-redux";

const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const activation_endpoint = 'http://' + getServer() + '/api/activation_instance/';
const rulebook_endpoint = 'http://' + getServer() + '/api/rulebooks/';
const inventories_endpoint = 'http://' + getServer() + '/api/inventories/';
const vars_endpoint = 'http://' + getServer() + '/api/extra_vars/';
const project_endpoint = 'http://' + getServer() + '/api/projects/';

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
  const [rulesets, setRuleSets] = useState<RuleType[]>([{id:'', name:intl.formatMessage(sharedMessages.ruleSetPlaceholder)}]);
  const [inventories, setInventories] = useState<InventoryType[]>([{id:'', name: intl.formatMessage(sharedMessages.inventoryPlaceholder) }]);
  const [extravars, setExtraVars] = useState<ExtraVarType[]>([{id:'', name:intl.formatMessage(sharedMessages.extraVarPlaceholder), extra_var:''}]);
  const [projects, setProjects] = useState<ExtraVarType[]>([{id:'', name:intl.formatMessage(sharedMessages.projectPlaceholder), extra_var:''}]);
  const [executionEnvironments, setExecutionEnvironments] = useState<ExecutionEnvironmentType[]>([{id:'',
    name:intl.formatMessage(sharedMessages.executionEnvironmentPlaceholder)}]);
  const [restartPolicies, setRestartPolicies] = useState<RestartPolicyType[]>([{id:'', name: intl.formatMessage(sharedMessages.restartPolicyPlaceholder)}]);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [executionEnvironment, setExecutionEnvironment] = useState('');
  const [restartPolicy, setRestartPolicy] = useState('');
  const [ruleset, setRuleSet] = useState('');
  const [inventory, setInventory] = useState('');
  const [extravar, setExtraVar] = useState('');
  const [project, setProject] = useState('');
  const [workingDirectory, setWorkingDirectory] = useState('');

  const [ validatedName, setValidatedName ] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [ validatedRuleSet, setValidatedRuleSet ] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [ validatedInventory, setValidatedInventory ] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [ validatedExtraVar, setValidatedExtraVar ] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [ validatedProject, setValidatedProject ] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [ validatedWorkingDirectory, setValidatedWorkingDirectory ] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [ validatedExecutionEnvironment, setValidatedExecutionEnvironment ] = useState<ValidatedOptions>(ValidatedOptions.default);

  const dispatch = useDispatch();

  useEffect(() => {
     fetch(rulebook_endpoint, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setRuleSets([...rulesets, ...data]));
  }, []);

  useEffect(() => {
     fetch(inventories_endpoint, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setInventories([...inventories, ...data]));
  }, []);

  useEffect(() => {
     fetch(vars_endpoint, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setExtraVars([...extravars, ...data]));
  }, []);

  useEffect(() => {
     fetch(project_endpoint, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setProjects([...projects, ...data]));
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

  const validateProject = (value) => {
    (!value || value.length < 1 ) ?
      setValidatedProject(ValidatedOptions.error) :
      setValidatedProject(ValidatedOptions.default)
  }
  const onProjectChange = (value) => {
    setProject(value);
    validateProject(value);
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
    validateRuleSet(ruleset);
    validateInventory(inventory);
    validateExtraVar(extravar);
    validateWorkingDirectory(workingDirectory);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    validateFields();
    postData(activation_endpoint, { name: name,
                         rulebook_id: ruleset,
                         inventory_id: inventory,
                         extra_var_id: extravar,
                         project_id: project,
                         working_directory: workingDirectory,
                         execution_environment: executionEnvironment})
      .then((data) => { history.push(`/activation/${data.id}`);
        dispatch(
          addNotification({
            variant: 'success',
            title: intl.formatMessage(sharedMessages.addActivation),
            dismissable: true,
            description: intl.formatMessage(sharedMessages.add_activation_success)
          })
        );
      })
      .catch((error) => {
        history.push(`/activations`);
        dispatch(
          addNotification({
            variant: 'danger',
            title: intl.formatMessage(sharedMessages.addActivation),
            dismissable: true,
            description: `${intl.formatMessage(sharedMessages.add_activation_failure)} ${error}`
          })
        );
      });
    }

  return (
  <React.Fragment>
    <TopToolbar
      breadcrumbs={[
        {
          title: 'Rulebook activations',
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
                <FormGroup style={{paddingRight: '30px'}}  label="Rule Set"
                           fieldId={`rule-set-${ruleset}`}
                           helperTextInvalid={ intl.formatMessage(sharedMessages.selectRuleSet) }
                           helperTextInvalidIcon={<ExclamationCircleIcon />}
                           validated={validatedRuleSet}>
                  <FormSelect value={ruleset}
                              onChange={onRuleSetChange}
                              validated={validatedRuleSet}
                              placeholder={ intl.formatMessage(sharedMessages.ruleSetPlaceholder) }
                              onBlur={(event) => validateRuleSet(ruleset)}
                              aria-label="FormSelect Input RuleSet">
                    {rulesets.map((option, index) => (
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
                <FormGroup style={{paddingRight: '30px'}}  label="Project"
                           fieldId={'activation-project'}
                           helperTextInvalid={ intl.formatMessage(sharedMessages.selectProject) }
                           helperTextInvalidIcon={<ExclamationCircleIcon />}
                           validated={validatedProject}>
                  <FormSelect value={project}
                              onChange={onProjectChange}
                              placeholder={ intl.formatMessage(sharedMessages.projectPlaceholder) }
                              onBlur={() => validateProject(project)}
                              validated={validatedProject}
                              aria-label="FormSelect Input Project">
                    {projects.map((option, index) => (
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
