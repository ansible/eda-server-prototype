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

interface IRemoveJob {
  ids?: Array<string|number>,
  fetchData: any,
  pagination?: PaginationConfiguration,
  setSelectedJobs: any
}
const jobEndpoint = 'http://' + getServer() + '/api/job_instance/';

export const fetchJob = (jobId, pagination=defaultSettings) =>
{
  return fetch(`${jobEndpoint}${jobId}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then(response => response.json());
}

const RemoveJob: React.ComponentType<IRemoveJob> = ( {ids = [],
                                             fetchData,
                                             pagination = defaultSettings,
                                             setSelectedJobs} ) => {
  const intl = useIntl();
  const [job, setJob] = useState<JobType>();
  const { id } = useParams<{id:string}>();
  const { push, goBack } = useHistory();

  const removeJob = async (jobId) =>
  {
    await removeData(`${jobEndpoint}${jobId}`);
    return fetchData(pagination);
  }

  const onSubmit = () => {
    removeJob(id).then(() => push('/jobs'));
  };

  useEffect(() => {
    fetchJob(id).then(data => setJob(data))
  }, []);

  return <Modal
      aria-label={
        intl.formatMessage(sharedMessages.jobRemoveTitle) as string
      }
      titleIconVariant="warning"
      title={intl.formatMessage(sharedMessages.jobRemoveTitle)}
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
            {intl.formatMessage(sharedMessages.jobRemoveDescription)}
          </Text>
        </TextContent>
      </StackItem>
      <StackItem>
        <TextContent>
          <Text component={TextVariants.p}>
            <strong>{ job?.name || `Job ${job?.id}` }</strong>
          </Text>
        </TextContent>
      </StackItem>
    </Stack>
  </Modal>
};

export { RemoveJob };
