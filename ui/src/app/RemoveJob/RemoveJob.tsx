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
import {getServer, removeData} from "@app/utils/utils";
import {defaultSettings} from "@app/shared/pagination";
import {JobType} from "@app/Job/Job";
import {useDispatch} from "react-redux";
import {addNotification} from "@redhat-cloud-services/frontend-components-notifications";
import {fetchProject} from "@app/RemoveProject/RemoveProject";

interface IRemoveJob {
  ids?: Array<string|number>,
  fetchData?: any,
  pagination?: PaginationConfiguration,
  resetSelectedJobs?: any
}
const jobEndpoint = 'http://' + getServer() + '/api/job_instance';

export const fetchJob = (jobId, pagination=defaultSettings) =>
{
  return fetch(`${jobEndpoint}/${jobId}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then(response => response.json());
}

const RemoveJob: React.ComponentType<IRemoveJob> = ( {ids = [],
                                             fetchData = null,
                                             pagination = defaultSettings,
                                             resetSelectedJobs = null} ) => {
  const intl = useIntl();
  const dispatch = useDispatch();
  const [job, setJob] = useState<JobType>();
  const { id } = useParams<{id:string}>();
  const { push, goBack } = useHistory();

  const removeId = id ? id : ( !id && ids && ids.length === 1 ) ? ids[0] : undefined;

  const removeJob = (jobId) => removeData(`${jobEndpoint}/${jobId}`);

  async function removeJobs(ids) {
    return Promise.all(
      ids.map(
        async (id) => await removeJob(id)
      )
    );
  }

  const onSubmit = () => {
    if ( !id && !(ids && ids.length > 0 )) {
      return;
    }
    (removeId ? removeJob(removeId) : removeJobs(ids))
    .catch((error) => {
      push('/jobs');
      dispatch(
        addNotification({
          variant: 'danger',
          title: intl.formatMessage(sharedMessages.jobRemoveTitle),
          dismissable: true,
          description: `${intl.formatMessage(sharedMessages.delete_job_failure)}  ${error}`
        })
      );
    }).then(() => push('/jobs'))
      .then(() => { if ( !id ) { resetSelectedJobs();} })
      .then(() => { if(fetchData) { fetchData(pagination) } })
  };

  useEffect(() => {
    fetchJob(id || removeId).then(data => setJob(data))
  }, [removeId]);

  return <Modal
      aria-label={
        intl.formatMessage(sharedMessages.jobRemoveTitle) as string
      }
      titleIconVariant="warning"
      title={ removeId ? intl.formatMessage(sharedMessages.jobRemoveTitle) : intl.formatMessage(sharedMessages.jobsRemoveTitle)}
      isOpen
      variant="small"
      onClose={goBack}
      actions={[
        <Button
          key="submit"
          variant="danger"
          type="button"
          id="confirm-delete-job"
          ouiaId="confirm-delete-job"
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
            { removeId ? intl.formatMessage(sharedMessages.jobRemoveDescription)
              : intl.formatMessage(sharedMessages.jobsRemoveDescription)}
          </Text>
        </TextContent>
      </StackItem>
      <StackItem>
        <TextContent>
          { removeId ? <Text component={TextVariants.p}>
            <strong> { job?.name || `Job ${job?.id}` } </strong>
          </Text> : <Text component={TextVariants.p}>
            <strong> { `${ids.length} selected`  } </strong>
          </Text>  }
        </TextContent>
      </StackItem>
    </Stack>
  </Modal>
};

export { RemoveJob };
