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
import {InventoryType} from "@app/Inventories/Inventories";
import {addNotification} from "@redhat-cloud-services/frontend-components-notifications";
import {useDispatch} from "react-redux";

interface IRemoveInventory {
  ids?: Array<string|number>,
  fetchData: any,
  pagination?: PaginationConfiguration,
  setSelectedInventories: any
}
const inventoryEndpoint = 'http://' + getServer() + '/api/inventory_instance/';

export const fetchInventory = (inventoryId, pagination=defaultSettings) =>
{
  return fetch(`${inventoryEndpoint}${inventoryId}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then(response => response.json());
}

const RemoveInventory: React.ComponentType<IRemoveInventory> = ( {ids = [],
                                             fetchData,
                                             pagination = defaultSettings,
                                             setSelectedInventories} ) => {
  const intl = useIntl();
  const dispatch = useDispatch();
  const [inventory, setInventory] = useState<InventoryType>();
  const { id } = useParams<{id:string}>();
  const { push, goBack } = useHistory();

  const removeInventory = async (inventoryId) =>
  {
    await removeData(`${inventoryEndpoint}${inventoryId}`);
    return fetchData(pagination);
  }

  const onSubmit = () => {
    removeInventory(id).then(() => push('/inventories'))
    .catch((err) => {
      dispatch(
        addNotification({
          variant: 'danger',
          title: intl.formatMessage(sharedMessages.inventoryRemoveTitle),
          dismissable: true,
          description: intl.formatMessage(sharedMessages.delete_inventory_failure)
        })
      );
    });
  };

  useEffect(() => {
    fetchInventory(id).then(data => setInventory(data))
  }, []);

  return <Modal
      aria-label={
        intl.formatMessage(sharedMessages.inventoryRemoveTitle) as string
      }
      titleIconVariant="warning"
      title={intl.formatMessage(sharedMessages.inventoryRemoveTitle)}
      isOpen
      variant="small"
      onClose={goBack}
      actions={[
        <Button
          key="submit"
          variant="danger"
          type="button"
          id="confirm-delete-inventory"
          ouiaId="confirm-delete-inventory"
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
            {intl.formatMessage(sharedMessages.inventoryRemoveDescription)}
          </Text>
        </TextContent>
      </StackItem>
      <StackItem>
        <TextContent>
          <Text component={TextVariants.p}>
            <strong>{ inventory?.name }</strong>
          </Text>
        </TextContent>
      </StackItem>
    </Stack>
  </Modal>
};

export { RemoveInventory };
