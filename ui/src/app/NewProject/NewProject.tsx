import {Grid, GridItem, PageSection, Title} from '@patternfly/react-core';
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

const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const endpoint = 'http://' + getServer() + '/api/projects/';

const NewProject: React.FunctionComponent = () => {

  const history = useHistory();

  const [scmUrl, setScmUrl] = useState('');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [scmType, setScmType] = useState('');
  const [scmCredential, setScmCredential] = useState('');
  const intl = useIntl();
  const dispatch = useDispatch();

  const handleSubmit = () => {
			postData(endpoint, { url: scmUrl, name: name, description: description })
				.then(data => {
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
              >
                <TextInput
                  onChange={setName}
                  value={name}
                  id="name"
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
              >
                <TextInput
                  onChange={setScmUrl}
                  value={scmUrl}
                  id="url-1"
                  placeholder={intl.formatMessage(sharedMessages.scmUrlPlaceholder)}
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
            <Button variant="primary" onClick={handleSubmit}>Save</Button>
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
