import { Grid, GridItem, PageSection, Title } from '@patternfly/react-core';
import { useHistory, useParams } from 'react-router-dom';
import React, { useEffect, useState } from 'react';
import { Card, CardBody as PFCardBody } from '@patternfly/react-core';
import { useIntl } from 'react-intl';
import { ActionGroup, Button, Form, FormGroup, TextInput } from '@patternfly/react-core';
import styled from 'styled-components';
import { TopToolbar } from '@app/shared/top-toolbar';
import sharedMessages from '../messages/shared.messages';
import { ProjectType } from '@app/shared/types/common-types';
import { addNotification } from '@redhat-cloud-services/frontend-components-notifications';
import { useDispatch } from 'react-redux';
import { fetchProject, updateProject } from '@app/API/Project';

const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
`;
const EditProject: React.FunctionComponent = () => {
  const history = useHistory();
  const [project, setProject] = useState<ProjectType>({ id: '', name: '' });
  const { id } = useParams<{ id: string }>();
  const intl = useIntl();
  const dispatch = useDispatch();

  useEffect(() => {
    fetchProject(id).then((data) => setProject(data.data));
  }, []);

  const setScmUrl = (url: string) => setProject({ ...project, url: url });
  const setName = (name: string) => setProject({ ...project, name: name });
  const setDescription = (description: string) => setProject({ ...project, description: description });
  const setScmType = (scm_type: string) => setProject({ ...project, scm_type: scm_type });
  const setScmToken = (scm_token: string) => setProject({ ...project, scm_token: scm_token });

  const handleSubmit = () => {
    updateProject(project)
      .then((data) => {
        history.push(`/project/${data?.data?.id}`);
        dispatch(
          addNotification({
            variant: 'success',
            title: intl.formatMessage(sharedMessages.editProject),
            dismissable: true,
            description: intl.formatMessage(sharedMessages.edit_project_success),
          })
        );
      })
      .catch((error) => {
        history.push(`/projects`);
        dispatch(
          addNotification({
            variant: 'danger',
            title: intl.formatMessage(sharedMessages.editProject),
            dismissable: true,
            description: `${intl.formatMessage(sharedMessages.edit_project_failure)}  ${error}`,
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
            to: '/projects',
          },
          {
            title: project?.name,
            key: 'details',
            to: `/project/${project?.id}/details`,
          },
          {
            title: 'Edit',
          },
        ]}
      >
        <Title headingLevel={'h2'}>{`${project?.name || 'project'}`}</Title>
      </TopToolbar>
      <PageSection>
        <Card>
          <CardBody>
            <Form>
              <Grid hasGutter>
                <GridItem span={4}>
                  <FormGroup style={{ paddingLeft: '15px', paddingRight: '15px' }} label="Name" fieldId="name">
                    <TextInput
                      onChange={setName}
                      value={project?.name}
                      id="name"
                      placeholder={intl.formatMessage(sharedMessages.namePlaceholder)}
                    />
                  </FormGroup>
                </GridItem>
                <GridItem span={4}>
                  <FormGroup
                    style={{ paddingLeft: '15px', paddingRight: '15px' }}
                    label="Description"
                    fieldId="description"
                  >
                    <TextInput
                      onChange={setDescription}
                      value={project?.description}
                      id="description"
                      placeholder={intl.formatMessage(sharedMessages.descriptionPlaceholder)}
                    />
                  </FormGroup>
                </GridItem>
                <GridItem span={4}>
                  <FormGroup style={{ paddingLeft: '15px', paddingRight: '15px' }} label="SCM type" fieldId="type">
                    <TextInput
                      onChange={setScmType}
                      value={project?.scm_type}
                      id="scmType"
                      placeholder={intl.formatMessage(sharedMessages.scmTypePlaceholder)}
                    />
                  </FormGroup>
                </GridItem>
                <GridItem span={4}>
                  <FormGroup style={{ paddingLeft: '15px', paddingRight: '15px' }} label="SCM URL" fieldId="url-1">
                    <TextInput
                      onChange={setScmUrl}
                      value={project?.url}
                      id="url-1"
                      placeholder={intl.formatMessage(sharedMessages.scmUrlPlaceholder)}
                    />
                  </FormGroup>
                </GridItem>
                <GridItem span={4}>
                  <FormGroup style={{ paddingLeft: '15px', paddingRight: '15px' }} label="SCM token" fieldId="scmToken">
                    <TextInput
                      onChange={setScmToken}
                      value={project?.scm_token}
                      id="scmToken"
                      placeholder={intl.formatMessage(sharedMessages.scmTokenPlaceholder)}
                    />
                  </FormGroup>
                </GridItem>
              </Grid>
              <ActionGroup>
                <Button variant="primary" onClick={handleSubmit}>
                  Save
                </Button>
                <Button variant="link" onClick={() => history.push('/projects')}>
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

export { EditProject };
