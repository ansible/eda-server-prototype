/* eslint-disable react/prop-types */
import React, {useEffect, useState} from 'react';
import {useHistory, useParams} from 'react-router-dom';
import {
  Modal,
  Button,
  Text,
  TextVariants,
  TextContent,
  Stack, StackItem
} from '@patternfly/react-core';
import {useIntl} from "react-intl";
import sharedMessages from "../messages/shared.messages";
import {ProjectType} from "@app/shared/types/common-types";
import {getServer, removeData} from "@app/utils/utils";
import {defaultSettings} from "@app/shared/pagination";
import {useDispatch} from "react-redux";
import {addNotification} from "@redhat-cloud-services/frontend-components-notifications";

interface IRemoveProject {
  ids?: Array<string|number>,
  fetchData?: any,
  pagination?: PaginationConfiguration,
  setSelectedProjects?: any
}
const projectEndpoint = 'http://' + getServer() + '/api/projects';

export const fetchProject = (projectId, pagination=defaultSettings) =>
{
  return fetch(`${projectEndpoint}/${projectId}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then(response => response.json());
}

const RemoveProject: React.ComponentType<IRemoveProject> = ( {ids = [],
                                             fetchData = null,
                                             pagination = defaultSettings,
                                             setSelectedProjects = null} ) => {
  const intl = useIntl();
  const dispatch = useDispatch();
  const [project, setProject] = useState<ProjectType>();
  const { id } = useParams<{id:string}>();
  const { push, goBack } = useHistory();

  const removeProject = (projectId) => removeData(`${projectEndpoint}/${projectId}`);

  const onSubmit = () => {
    removeProject(id).then(() => { if(fetchData) { fetchData(pagination)} push('/projects');})
    .catch((error) => {
      if(fetchData) { fetchData(pagination) }
      push('/projects');
      dispatch(
        addNotification({
          variant: 'danger',
          title: intl.formatMessage(sharedMessages.projectRemoveTitle),
          dismissable: true,
          description: `${intl.formatMessage(sharedMessages.delete_project_failure)}  ${error}`
        })
      );
    });
  };

  useEffect(() => {
    fetchProject(id).then(data => setProject(data))
  }, []);

  return <Modal
      aria-label={
        intl.formatMessage(sharedMessages.projectRemoveTitle) as string
      }
      titleIconVariant="warning"
      title={intl.formatMessage(sharedMessages.projectRemoveTitle)}
      isOpen
      variant="small"
      onClose={goBack}
      actions={[
        <Button
          key="submit"
          variant="danger"
          type="button"
          id="confirm-delete-project"
          ouiaId="confirm-delete-project"
          onClick={onSubmit}
        >
          {intl.formatMessage(sharedMessages.delete)}
        </Button>,
        <Button
          key="cancel"
          ouiaId="cancel"
          variant="link"
          type="button"
          onClick={goBack}
        >
          {intl.formatMessage(sharedMessages.cancel)}
        </Button>
      ]}
    >
    <Stack hasGutter>
      <StackItem>
        <TextContent>
          <Text component={TextVariants.p}>
            {intl.formatMessage(sharedMessages.projectRemoveDescription)}
          </Text>
        </TextContent>
      </StackItem>
      <StackItem>
        <TextContent>
          <Text component={TextVariants.p}>
            <strong> { project?.name } </strong>
          </Text>
        </TextContent>
      </StackItem>
    </Stack>
  </Modal>
};

export { RemoveProject };
