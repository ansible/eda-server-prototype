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
import {ActivationType} from "@app/Activations/Activations";
import {addNotification} from "@redhat-cloud-services/frontend-components-notifications";
import {useDispatch} from "react-redux";

interface IRemoveActivation {
  ids?: Array<string|number>,
  fetchData?: any,
  pagination?: PaginationConfiguration,
  setSelectedActivations?: any
}
const activationEndpoint = 'http://' + getServer() + '/api/activation_instance/';

export const fetchActivation = (activationId, pagination=defaultSettings) =>
{
  return fetch(`${activationEndpoint}${activationId}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then(response => response.json());
}

const RemoveActivation: React.ComponentType<IRemoveActivation> = ( {ids = [],
                                             fetchData = null,
                                             pagination = defaultSettings,
                                             setSelectedActivations = null } ) => {
  const intl = useIntl();
  const dispatch = useDispatch();
  const [activation, setActivation] = useState<ActivationType>();
  const { id } = useParams<{id:string}>();
  const { push, goBack } = useHistory();

  const removeActivation = async (activationId) =>
    removeData(`${activationEndpoint}${activationId}`);

  const onSubmit = () => {
    removeActivation(id).then(() => { if(fetchData) { fetchData(pagination);} push('/activations');})
    .catch((error) => {
        if(fetchData) {
          fetchData(pagination);
        }
        dispatch(
          addNotification({
            variant: 'danger',
            title: intl.formatMessage(sharedMessages.activationRemoveTitle),
            dismissable: true,
            description: `${intl.formatMessage(sharedMessages.delete_activation_failure)}  ${error}`
          })
        );
        push('/activations');
      });
  };

  useEffect(() => {
    fetchActivation(id).then(data => setActivation(data))
  }, []);

  return <Modal
      aria-label={
        intl.formatMessage(sharedMessages.activationRemoveTitle) as string
      }
      titleIconVariant="warning"
      title={intl.formatMessage(sharedMessages.activationRemoveTitle)}
      isOpen
      variant="small"
      onClose={goBack}
      actions={[
        <Button
          key="submit"
          variant="danger"
          type="button"
          id="confirm-delete-activation"
          ouiaId="confirm-delete-activation"
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
            {intl.formatMessage(sharedMessages.activationRemoveDescription)}
          </Text>
        </TextContent>
      </StackItem>
      <StackItem>
        <TextContent>
          <Text component={TextVariants.p}>
            <strong>{ activation?.name }</strong>
          </Text>
        </TextContent>
      </StackItem>
    </Stack>
  </Modal>
};

export { RemoveActivation };
