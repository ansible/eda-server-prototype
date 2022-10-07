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
import {addNotification} from '@redhat-cloud-services/frontend-components-notifications';
import {useDispatch} from "react-redux";

const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const SimpleList = styled(PFSimpleList)`
  white-space: pre-wrap;
`

const endpoint_job = 'http://' + getServer() + '/api/job_instance/';
const endpoint_playbooks = 'http://' + getServer() + '/api/playbooks/';
const endpoint_inventories = 'http://' + getServer() + '/api/inventories/';
const endpoint_vars = 'http://' + getServer() + '/api/extra_vars/';

const NewJob: React.FunctionComponent = () => {
  const history = useHistory();
  const intl = useIntl();
  const dispatch = useDispatch();
  const [playbooks, setPlaybooks] = useState([{"id": 0, "name": "Please select a playbook"}])
  const [inventories, setInventories] = useState([{"id": 0, "name": "Please select an inventory"}]);
  const [extravars, setExtraVars] = useState([{"id": 0, "name": "Please select vars"}]);
  const [name, setName] = useState();
  const [playbook, setPlaybook] = useState('');
  const [inventory, setInventory] = useState('');
  const [extravar, setExtraVar] = useState('');

  const [ validatedName, setValidatedName ] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [ validatedPlaybook, setValidatedPlaybook ] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [ validatedInventory, setValidatedInventory ] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [ validatedExtraVar, setValidatedExtraVar ] = useState<ValidatedOptions>(ValidatedOptions.default);
  useEffect(() => {
     fetch(endpoint_playbooks, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then(data => setPlaybooks([...playbooks, ...data]));
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

  const validatePlaybook = (value) => {
    (!value || value.length < 1 ) ?
      setValidatedPlaybook(ValidatedOptions.error) :
      setValidatedPlaybook(ValidatedOptions.default)
  };

  const onPlaybookChange = (value) => {
    setPlaybook(value);
    validatePlaybook(value);
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
    validatePlaybook(playbook);
    validateInventory(inventory);
    validateExtraVar(extravar);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    validateFields();
    postData(endpoint_job, { name: name,
                         playbook_id: playbook,
                         inventory_id: inventory,
                         extra_var_id: extravar})
      .then(data => {
        data?.id ? history.push(`/job/${data.id}`) :
          history.push(`/jobs`);
        dispatch(
          addNotification({
            variant: 'success',
            title: intl.formatMessage(sharedMessages.addJob),
            dismissable: true,
            description: intl.formatMessage(sharedMessages.add_job_success)
          })
        );
      }).catch((err) => {
      history.push(`/jobs`);
      dispatch(
        addNotification({
          variant: 'danger',
          title: intl.formatMessage(sharedMessages.addJob),
          dismissable: true,
          description: intl.formatMessage(sharedMessages.add_job_failure)
        })
      );
    });
  };

  return (
  <React.Fragment>
    <TopToolbar
      breadcrumbs={[
        {
          title: 'Jobs',
          to: '/jobs'
        }
      ]
      }>
      <Title headingLevel={"h2"}>Add new job</Title>
    </TopToolbar>
    <PageSection>
      <Card>
        <CardBody>
          <Form>
            <Text component={TextVariants.small}>
              { intl.formatMessage(sharedMessages.allFieldsRequired) }
            </Text>
            <FormGroup label="Playbook"
                       fieldId={`job-playbook-${playbook}`}
                       helperTextInvalid={ intl.formatMessage(sharedMessages.selectPlaybook) }
                       helperTextInvalidIcon={<ExclamationCircleIcon />}
                       validated={validatedPlaybook}>
              <FormSelect value={playbook}
                          onChange={onPlaybookChange}
                          validated={validatedPlaybook}
                          onBlur={(event) => validatePlaybook(playbook)}
                          aria-label="FormSelect Input Playbook">
                {playbooks.map((option, index) => (
                  <FormSelectOption
                    key={index}
                    value={option.id}
                    label={"" + option.id + " "+ option.name} />
                ))}
              </FormSelect>
            </FormGroup>
            <FormGroup label="Inventory"
                       fieldId={'job-inventory'}
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
                       fieldId={'job-vars'}
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

export { NewJob };
