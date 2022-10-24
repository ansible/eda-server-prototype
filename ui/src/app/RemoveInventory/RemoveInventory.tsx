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
import {fetchInventory, removeInventory} from "@app/API/Inventory";

interface IRemoveInventory {
  ids?: Array<string|number>,
  fetchData: any,
  pagination?: PaginationConfiguration,
  resetSelectedInventories?: any
}

const RemoveInventory: React.ComponentType<IRemoveInventory> = ( {ids = [],
                                             fetchData = null,
                                             pagination = defaultSettings,
                                             resetSelectedInventories} ) => {
  const intl = useIntl();
  const dispatch = useDispatch();
  const [inventory, setInventory] = useState<InventoryType>();
  const { id } = useParams<{id:string}>();
  const { push, goBack } = useHistory();

  const removeId = id ? id : ( !id && ids && ids.length === 1 ) ? ids[0] : undefined;

  async function removeInventories(ids) {
    return Promise.all(
      ids.map(
        async (id) => await removeInventory(id)
      )
    );
  }

  const onSubmit = () => {
    if ( !id && !(ids && ids.length > 0 )) {
      return;
    }
    (removeId ? removeInventory(removeId) : removeInventories(ids))
    .catch((error) => {
      push('/inventories');
      dispatch(
        addNotification({
          variant: 'danger',
          title: intl.formatMessage(sharedMessages.inventoryRemoveTitle),
          dismissable: true,
          description: `${intl.formatMessage(sharedMessages.delete_inventory_failure)}  ${error}`
        })
      );
    }).then(() => push('/inventories'))
      .then(() => { if ( !id ) { resetSelectedInventories();} })
      .then(() => { if(fetchData) { fetchData(pagination) } })
  };

  useEffect(() => {
    if( !id && !removeId) {
      return;
    }
    fetchInventory(id ? id : removeId).then(data => setInventory(data))
  }, [removeId]);

  return <Modal
      aria-label={
        intl.formatMessage(sharedMessages.inventoryRemoveTitle) as string
      }
      titleIconVariant="warning"
      title={ removeId ? intl.formatMessage(sharedMessages.inventoryRemoveTitle) : intl.formatMessage(sharedMessages.inventoriesRemoveTitle)}
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
            { removeId ? intl.formatMessage(sharedMessages.inventoryRemoveDescription)
              : intl.formatMessage(sharedMessages.inventoriesRemoveDescription)}
          </Text>
        </TextContent>
      </StackItem>
      <StackItem>
        <TextContent>
          { removeId ? <Text component={TextVariants.p}>
            <strong> { inventory?.name } </strong>
          </Text> : <Text component={TextVariants.p}>
            <strong> { `${ids.length} selected`  } </strong>
          </Text>  }
        </TextContent>
      </StackItem>
    </Stack>
  </Modal>
};

export { RemoveInventory };
