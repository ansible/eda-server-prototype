import { Card, CardBody as PFCardBody, Form, PageSection, Title, ValidatedOptions } from '@patternfly/react-core';
import { useHistory } from 'react-router-dom';
import React, { useEffect, useState } from 'react';
import styled from 'styled-components';
import { TopToolbar } from '@app/shared/top-toolbar';
import { useIntl } from 'react-intl';
import sharedMessages from '../messages/shared.messages';
import 'ace-builds/src-noconflict/theme-kuroir';
import { addNotification } from '@redhat-cloud-services/frontend-components-notifications';
import { useDispatch } from 'react-redux';
import { addInventory } from '@app/API/Inventory';
import InventoryForm from './shared/InventoryForm';

const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
`;
const NewInventory: React.FunctionComponent = () => {
  const history = useHistory();
  const intl = useIntl();
  const dispatch = useDispatch();
  const [error, setError] = useState(null);

  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
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
        <Title headingLevel={'h2'}>Add new inventory</Title>
      </TopToolbar>
      <PageSection>
        <Card>
          <CardBody>
            <Form>
              <InventoryForm
                handleSubmit={(name, inventory, description) => handleSubmit(name, inventory, description)}
                isSubmitting={isSubmitting}
              />
            </Form>
          </CardBody>
        </Card>
      </PageSection>
    </React.Fragment>
  );
};

export { NewInventory };
