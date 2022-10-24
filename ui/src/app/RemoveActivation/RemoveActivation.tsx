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
import {defaultSettings} from "@app/shared/pagination";
import {ActivationType} from "@app/Activations/Activations";
import {addNotification} from "@redhat-cloud-services/frontend-components-notifications";
import {useDispatch} from "react-redux";
import {fetchActivation, IRemoveActivation, removeActivation} from "@app/API/Activation";

const RemoveActivation: React.ComponentType<IRemoveActivation> = ( {ids = [],
                                             fetchData = null,
                                             pagination = defaultSettings,
                                             resetSelectedActivations = null } ) => {
  const intl = useIntl();
  const dispatch = useDispatch();
  const [activation, setActivation] = useState<ActivationType>();
  const { id } = useParams<{id:string}>();
  const { push, goBack } = useHistory();

  const removeId = id ? id : ( !id && ids && ids.length === 1 ) ? ids[0] : undefined;

  async function removeActivations(ids) {
    return Promise.all(
      ids.map(
        async (id) => await removeActivation(id)
      )
    );
  }

  const onSubmit = () => {
    if ( !id && !(ids && ids.length > 0 )) {
      return;
    }

    ( removeId ? removeActivation(removeId) : removeActivations(ids))
      .catch((error) => {
        //TODO - when the endpoint error on POST is fixed, remove the fetch data and the resetSelected activations on error
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
      })
      .then(() => push('/activations'))
      .then(() => { if ( !id ) { resetSelectedActivations();} })
      .then(() => { if(fetchData) { fetchData(pagination) } });
  };

  useEffect(() => {
    fetchActivation(id || removeId).then(data => setActivation(data))
  }, [removeId]);

  return <Modal
      aria-label={
        intl.formatMessage(sharedMessages.activationRemoveTitle) as string
      }
      titleIconVariant="warning"
      title={ removeId ? intl.formatMessage(sharedMessages.activationRemoveTitle) : intl.formatMessage(sharedMessages.activationsRemoveTitle)}
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
            { removeId ? intl.formatMessage(sharedMessages.activationRemoveDescription)
              : intl.formatMessage(sharedMessages.activationsRemoveDescription)}
          </Text>
        </TextContent>
      </StackItem>
      <StackItem>
        <TextContent>
          { removeId ? <Text component={TextVariants.p}>
            <strong> { activation?.name } </strong>
          </Text> : <Text component={TextVariants.p}>
            <strong> { `${ids.length} selected`  } </strong>
          </Text>  }
        </TextContent>
      </StackItem>
    </Stack>
  </Modal>
};

export { RemoveActivation };
