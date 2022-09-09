import {Grid, GridItem, PageSection, Title} from '@patternfly/react-core';
import {useHistory, useParams} from "react-router-dom";
import React, {useEffect, useState} from 'react';
import {
  Card,
  CardBody as PFCardBody
} from '@patternfly/react-core';
import {useIntl} from "react-intl";
import { ActionGroup, Button, Form, FormGroup, TextInput } from '@patternfly/react-core';
import {patchData, getServer} from '@app/utils/utils';
import styled from 'styled-components';
import {TopToolbar} from "@app/shared/top-toolbar";
import sharedMessages from "../messages/shared.messages";
import {ProjectType} from "@app/shared/types/common-types";

const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const endpoint = 'http://' + getServer() + '/api/projects/';

const EditProject: React.FunctionComponent = () => {
  const history = useHistory();
  const [project, setProject] = useState<ProjectType>({id: '', name: '' });
  const { id } = useParams<{id:string}>();
  const intl = useIntl();

  useEffect(() => {
    fetch(endpoint + id, {
      headers: {
        'Content-Type': 'application/json',
      },
    }).then(response => response.json())
      .then(data => setProject(data));
  }, []);

  console.log('Debug - project: ', project);
  const setScmUrl = (url: string) =>  setProject({...project, url: url} );
  const setName = (name: string) =>  setProject({...project, name: name} );
  const setDescription = (description: string) =>  setProject({...project, description: description} );
  const setScmType = (scm_type: string) =>  setProject({...project, scm_type: scm_type} );
  const setScmToken = (scm_token: string) => setProject({...project, scm_token: scm_token} );

  const handleSubmit = () => {
			patchData(`${endpoint}${project.id}`, { name: project.name })
				.then(data => {
          history.push(`/project/${data.id}`);
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
          title: 'Edit'
        }
        ]
      }>
      <Title headingLevel={"h2"}>{ `${project?.name || 'project'}`}</Title>
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
                  value={project?.name}
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
                  value={project?.description}
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
                  value={project?.scm_type}
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
                  value={project?.url}
                  id="url-1"
                  placeholder={intl.formatMessage(sharedMessages.scmUrlPlaceholder)}
                />
              </FormGroup>
            </GridItem>
            <GridItem span={4}>
              <FormGroup style={{paddingLeft: '15px', paddingRight: '15px'}}
                label="SCM token"
                fieldId="scmToken"
              >
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

export { EditProject };
