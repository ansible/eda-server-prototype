import {Grid, GridItem, PageSection, Title, ValidatedOptions} from '@patternfly/react-core';
import { useHistory } from "react-router-dom";
import React, { useState, useEffect } from 'react';
import {
  Card,
  CardBody as PFCardBody
} from '@patternfly/react-core';
import {useIntl} from "react-intl";
import {ActionGroup, Button, Form, FormGroup, TextInput} from '@patternfly/react-core';
import {postData} from '@app/utils/utils';
import {getServer} from '@app/utils/utils';
import styled from 'styled-components';
import {TopToolbar} from "@app/shared/top-toolbar";
import sharedMessages from "../messages/shared.messages";
import {addNotification} from '@redhat-cloud-services/frontend-components-notifications';
import {useDispatch} from "react-redux";
import {ExclamationCircleIcon} from "@patternfly/react-icons";
import {addProject} from "@app/API/Project";

const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const NewProject: React.FunctionComponent = () => {

  const history = useHistory();

  const [scmUrl, setScmUrl] = useState('');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [scmType, setScmType] = useState('');
  const [scmCredential, setScmCredential] = useState('');
  const [validatedName, setValidatedName ] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [validatedScmUrl, setValidatedScmUrl ] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const intl = useIntl();
  const dispatch = useDispatch();

  const validateName = (value): boolean => {
    if (!value || (value.length < 1)) {
      setValidatedName(ValidatedOptions.error);
      return false;
    } else {
      setValidatedName(ValidatedOptions.default);
      return true;
    }
  }

  const onNameChange = (value) => {
    setName(value);
    validateName(value);
  };

  const validateScmUrl = (value): boolean => {
    if(!value || value.length < 1 ) {
      setValidatedScmUrl(ValidatedOptions.error);
      return false;
    }else {
      setValidatedScmUrl(ValidatedOptions.default);
      return true;
    }
  }

  const onScmUrlChange = (value) => {
    setScmUrl(value);
    validateScmUrl(value);
  };

  const validateFields = () => {
    return validateName(name) &&
      validateScmUrl(scmUrl);
  }

  const handleSubmit = () => {
    if(!validateFields() ) {
      return;
    }
    setIsSubmitting(true);
    addProject({ url: scmUrl, name: name, description: description })
				.then(data => {
          setIsSubmitting(false);
          history.push(`/project/${data.id}`);
          dispatch(
            addNotification({
              variant: 'success',
              title: intl.formatMessage(sharedMessages.add_new_project),
              dismissable: true,
              description: intl.formatMessage(sharedMessages.add_project_success)
            })
          );
			}).catch((error) => {
      setIsSubmitting(false);
        history.push(`/projects`);
        dispatch(
          addNotification({
            variant: 'danger',
            title: intl.formatMessage(sharedMessages.add_new_project),
            dismissable: true,
            description: `${intl.formatMessage(sharedMessages.add_project_failure)}  ${error}`
          })
        );
      });
  };

  return (
  <React.Fragment>
    <TopToolbar
      breadcrumbs={[
        {
          title: intl.formatMessage(sharedMessages.projects),
          to: '/projects'
        },
        {
          title: 'Add'
        }
        ]
      }>
      <Title headingLevel={"h2"}>{ intl.formatMessage(sharedMessages.add_new_project)}</Title>
    </TopToolbar>
    <PageSection>
      <Card>
        <CardBody>
        <Form>
          <Grid hasGutter>
            <GridItem span={4}>
              <FormGroup style={{paddingLeft: '15px', paddingRight: '15px'}}
                label="Name"
                fieldId="name"
                isRequired
                helperTextInvalid={ intl.formatMessage(sharedMessages.enterProjectName) }
                helperTextInvalidIcon={<ExclamationCircleIcon />}
                validated={validatedName}
              >
                <TextInput
                  id="project-name"
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
              <FormGroup style={{paddingLeft: '15px', paddingRight: '15px'}}
                label="Description"
                fieldId="description"
              >
                <TextInput
                  onChange={setDescription}
                  value={description}
                  id="description"
                  placeholder={intl.formatMessage(sharedMessages.descriptionPlaceholder)}
                />
              </FormGroup>
            </GridItem>
            <GridItem span={4}>
              <FormGroup style={{paddingLeft: '15px', paddingRight: '15px'}}
                label="SCM type"
                fieldId="type"
              >
                <TextInput
                  onChange={setScmType}
                  value={scmType}
                  id="scmType"
                  placeholder={intl.formatMessage(sharedMessages.scmTypePlaceholder)}
                />
              </FormGroup>
            </GridItem>
            <GridItem span={4}>
              <FormGroup style={{paddingLeft: '15px', paddingRight: '15px'}}
                label="SCM URL"
                fieldId="url-1"
                isRequired
                helperTextInvalid={ intl.formatMessage(sharedMessages.enterScmUrl) }
                helperTextInvalidIcon={<ExclamationCircleIcon />}
                validated={validatedScmUrl}
              >
                <TextInput
                  value={scmUrl}
                  id="url-1"
                  placeholder={intl.formatMessage(sharedMessages.scmUrlPlaceholder)}
                  label="SCM URL"
                  isRequired
                  validated={validatedScmUrl}
                  onChange={onScmUrlChange}
                  onBlur={(event) => validateScmUrl(scmUrl)}
                />
              </FormGroup>
            </GridItem>
            <GridItem span={4}>
              <FormGroup style={{paddingLeft: '15px', paddingRight: '15px'}}
                label="SCM credential"
                fieldId="scmCredential"
              >
                <TextInput
                  onChange={setScmCredential}
                  value={scmCredential}
                  id="scmCredential"
                  placeholder={intl.formatMessage(sharedMessages.scmTokenPlaceholder)}
                />
              </FormGroup>
            </GridItem>
          </Grid>
          <ActionGroup>
            <Button
              variant="primary"
              onClick={handleSubmit}
              isLoading={isSubmitting}
              isDisabled={isSubmitting}>
              {isSubmitting ? 'Adding ' : 'Add'}
            </Button>
            <Button variant="link" onClick={() => history.push('/projects')}>Cancel</Button>
          </ActionGroup>
        </Form>
        </CardBody>
      </Card>
    </PageSection>
  </React.Fragment>
)
}

export { NewProject };
