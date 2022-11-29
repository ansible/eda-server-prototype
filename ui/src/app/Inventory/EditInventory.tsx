import { Card, CardBody as PFCardBody, Form, PageSection, Title, ValidatedOptions } from '@patternfly/react-core';
import { useHistory, useParams } from 'react-router-dom';
import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { TopToolbar } from '@app/shared/top-toolbar';
import { useIntl } from 'react-intl';
import sharedMessages from '../messages/shared.messages';
import 'ace-builds/src-noconflict/theme-kuroir';
import { addNotification } from '@redhat-cloud-services/frontend-components-notifications';
import { useDispatch } from 'react-redux';
import { addInventory, fetchInventory } from '@app/API/Inventory';
import InventoryForm from './shared/InventoryForm';
import { InventoryType } from './inventory';
interface ParamsType {
  id: string;
}
const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
`;
const EditInventory: React.FunctionComponent = () => {
  const history = useHistory();
  const intl = useIntl();
  const dispatch = useDispatch();
  const params = useParams<ParamsType>();
  const [inventory, setInventory] = useState<InventoryType>();
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const fetchInventoryDetails = async () => {
    try {
      const { data } = await fetchInventory(params.id);
      console.log(data);
      setInventory(data);
    } catch (err: any) {
      setError(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchInventoryDetails();
  }, [history.location]);

  const validateName = (value: string) => {
    if (!value || value.length < 1) {
      throw new Error('Name is a required field');
    }
  };

  const validateInventory = (value: string) => {
    if (!value || value.length < 1) {
      throw new Error('Inventory is a required field');
    }
  };

  const validateFields = (name: string, inventory: string) => {
    try {
      validateName(name);
      validateInventory(inventory);
    } catch (err: any) {
      setError(err);
    }
  };

  const handleSubmit = async (name: string, inventory: string, description?: string | undefined) => {
    try {
      setIsSubmitting(true);
      validateFields(name, inventory);
      addInventory({ name, description, inventory }).then((data) => {
        data?.data?.id ? history.push(`/inventory/${data?.data?.id}`) : history.push(`/inventories`);
        dispatch(
          addNotification({
            variant: 'success',
            title: intl.formatMessage(sharedMessages.addInventory),
            dismissable: true,
            description: intl.formatMessage(sharedMessages.add_inventory_success),
          })
        );
      });
    } catch (error) {
      dispatch(
        addNotification({
          variant: 'danger',
          title: intl.formatMessage(sharedMessages.addInventory),
          dismissable: true,
          description: `${intl.formatMessage(sharedMessages.add_inventory_failure)}  ${error}`,
        })
      );
    }
  };
  if (isLoading || !inventory) {
    return <div> Loading</div>;
  }
  return (
    <React.Fragment>
      <TopToolbar
        breadcrumbs={[
          {
            title: 'Inventories',
            to: '/inventories',
            key: 'inventories',
          },
          {
            title: 'Add',
            key: 'inventory-add',
          },
        ]}
      >
        <Title headingLevel={'h2'}>Edit inventory</Title>
      </TopToolbar>
      <PageSection>
        <Card>
          <CardBody>
            <Form>
              <InventoryForm
                handleSubmit={(name, inventory, description) => handleSubmit(name, inventory, description)}
                isSubmitting={isSubmitting}
                inventory={inventory}
              />
            </Form>
          </CardBody>
        </Card>
      </PageSection>
    </React.Fragment>
  );
};
export { EditInventory };
