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
  Text,
  TextVariants,
  Title,
  ValidatedOptions,
} from '@patternfly/react-core';
import { useHistory } from 'react-router-dom';
import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { TopToolbar } from '@app/shared/top-toolbar';
import { ExclamationCircleIcon } from '@patternfly/react-icons';
import { useIntl } from 'react-intl';
import sharedMessages from '../messages/shared.messages';
import { addNotification } from '@redhat-cloud-services/frontend-components-notifications';
import { useDispatch } from 'react-redux';
import { listInventories } from '@app/API/Inventory';
import { listExtraVars } from '@app/API/Extravar';
import { listPlaybooks } from '@app/API/Playbook';
import { addJob } from '@app/API/Job';

const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
`;
const NewJob: React.FunctionComponent = () => {
  const history = useHistory();
  const intl = useIntl();
  const dispatch = useDispatch();
  const [playbooks, setPlaybooks] = useState([{ id: 0, name: 'Please select a playbook' }]);
  const [inventories, setInventories] = useState([{ id: 0, name: 'Please select an inventory' }]);
  const [extravars, setExtraVars] = useState([{ id: 0, name: 'Please select vars' }]);
  const [playbook, setPlaybook] = useState('');
  const [inventory, setInventory] = useState('');
  const [extravar, setExtraVar] = useState('');
  const [validatedPlaybook, setValidatedPlaybook] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [validatedInventory, setValidatedInventory] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [validatedExtraVar, setValidatedExtraVar] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  useEffect(() => {
    listPlaybooks().then((data) => setPlaybooks([...playbooks, ...data]));
  }, []);

  useEffect(() => {
    listInventories().then((data) => setInventories([...inventories, ...data]));
  }, []);

  useEffect(() => {
    listExtraVars().then((data) => setExtraVars([...extravars, ...data]));
  }, []);

  const validatePlaybook = (value): boolean => {
    if (!value || value.length < 1) {
      setValidatedPlaybook(ValidatedOptions.error);
      return false;
    } else {
      setValidatedPlaybook(ValidatedOptions.default);
      return true;
    }
  };

  const onPlaybookChange = (value) => {
    setPlaybook(value);
    validatePlaybook(value);
  };

  const validateInventory = (value): boolean => {
    if (!value || value.length < 1) {
      setValidatedInventory(ValidatedOptions.error);
      return false;
    } else {
      setValidatedInventory(ValidatedOptions.default);
      return true;
    }
  };

  const onInventoryChange = (value) => {
    setInventory(value);
    validateInventory(value);
  };

  const validateExtraVar = (value): boolean => {
    if (!value || value.length < 1) {
      setValidatedExtraVar(ValidatedOptions.error);
      return false;
    } else {
      setValidatedExtraVar(ValidatedOptions.default);
      return true;
    }
  };

  const onExtraVarChange = (value) => {
    setExtraVar(value);
    validateExtraVar(value);
  };

  const validateFields = () => {
    return validatePlaybook(playbook) && validateInventory(inventory) && validateExtraVar(extravar);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validateFields()) return;
    setIsSubmitting(true);
    addJob({
      name: '',
      playbook_id: playbook,
      inventory_id: inventory,
      extra_var_id: extravar,
    })
      .then((data) => {
        setIsSubmitting(false);
        data?.id ? history.push(`/job/${data.id}`) : history.push(`/jobs`);
        dispatch(
          addNotification({
            variant: 'success',
            title: intl.formatMessage(sharedMessages.addJob),
            dismissable: true,
            description: intl.formatMessage(sharedMessages.add_job_success),
          })
        );
      })
      .catch((error) => {
        setIsSubmitting(false);
        history.push(`/jobs`);
        dispatch(
          addNotification({
            variant: 'danger',
            title: intl.formatMessage(sharedMessages.addJob),
            dismissable: true,
            description: `${intl.formatMessage(sharedMessages.add_job_failure)}  ${error}`,
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
            to: '/jobs',
          },
        ]}
      >
        <Title headingLevel={'h2'}>Add new job</Title>
      </TopToolbar>
      <PageSection>
        <Card>
          <CardBody>
            <Form>
              <Text component={TextVariants.small}>{intl.formatMessage(sharedMessages.allFieldsRequired)}</Text>
              <FormGroup
                label="Playbook"
                fieldId={`job-playbook-${playbook}`}
                helperTextInvalid={intl.formatMessage(sharedMessages.selectPlaybook)}
                helperTextInvalidIcon={<ExclamationCircleIcon />}
                validated={validatedPlaybook}
              >
                <FormSelect
                  value={playbook}
                  onChange={onPlaybookChange}
                  validated={validatedPlaybook}
                  onBlur={(event) => validatePlaybook(playbook)}
                  aria-label="FormSelect Input Playbook"
                >
                  {playbooks.map((option, index) => (
                    <FormSelectOption key={index} value={option.id} label={'' + option.id + ' ' + option.name} />
                  ))}
                </FormSelect>
              </FormGroup>
              <FormGroup
                label="Inventory"
                fieldId={'job-inventory'}
                helperTextInvalid={intl.formatMessage(sharedMessages.selectInventory)}
                helperTextInvalidIcon={<ExclamationCircleIcon />}
                validated={validatedInventory}
              >
                <FormSelect
                  value={inventory}
                  onChange={onInventoryChange}
                  onBlur={() => validateInventory(inventory)}
                  validated={validatedInventory}
                  aria-label="FormSelect Input Inventory"
                >
                  {inventories.map((option, index) => (
                    <FormSelectOption key={index} value={option.id} label={'' + option.id + ' ' + option.name} />
                  ))}
                </FormSelect>
              </FormGroup>
              <FormGroup
                label="Extra Vars"
                fieldId={'job-vars'}
                helperTextInvalid={intl.formatMessage(sharedMessages.selectExtraVar)}
                helperTextInvalidIcon={<ExclamationCircleIcon />}
                validated={validatedExtraVar}
              >
                <FormSelect
                  value={extravar}
                  onChange={onExtraVarChange}
                  onBlur={() => validateExtraVar(extravar)}
                  validated={validatedExtraVar}
                  aria-label="FormSelect Input ExtraVar"
                >
                  {extravars.map((option, index) => (
                    <FormSelectOption key={index} value={option.id} label={'' + option.id + ' ' + option.name} />
                  ))}
                </FormSelect>
              </FormGroup>
              <ActionGroup>
                <Button variant="primary" onClick={handleSubmit} isLoading={isSubmitting} isDisabled={isSubmitting}>
                  {isSubmitting ? 'Adding ' : 'Add'}
                </Button>
                <Button variant="link" onClick={() => history.push('/activations')}>
                  {' '}
                  Cancel
                </Button>
              </ActionGroup>
            </Form>
          </CardBody>
        </Card>
      </PageSection>
    </React.Fragment>
  );
};

export { NewJob };
