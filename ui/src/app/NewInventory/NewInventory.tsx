import {
  ActionGroup,
  Button,
  Card,
  CardBody as PFCardBody,
  Form,
  FormGroup,
  Grid, GridItem,
  PageSection,
  TextInput,
  Title,
  ValidatedOptions
} from '@patternfly/react-core';
import {useHistory} from "react-router-dom";
import React, {useEffect, useState} from 'react';
import {getServer, postData} from '@app/utils/utils';
import styled from 'styled-components';
import {TopToolbar} from "@app/shared/top-toolbar";
import {ExclamationCircleIcon} from "@patternfly/react-icons";
import {useIntl} from "react-intl";
import sharedMessages from "../messages/shared.messages";

const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const endpoint_inventory = 'http://' + getServer() + '/api/inventory/';
const endpoint_inventories = 'http://' + getServer() + '/api/inventories/';


const NewInventory: React.FunctionComponent = () => {
  const history = useHistory();
  const intl = useIntl();
    const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [inventory, setInventory] = useState('');

  const [ validatedName, setValidatedName ] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [ validatedInventory, setValidatedInventory ] = useState<ValidatedOptions>(ValidatedOptions.default);

  useEffect(() => {
     fetch(endpoint_inventory, {
       headers: {
         'Content-Type': 'application/json',
       },
     }).then(response => response.json())
    .then((data) => setInventory(data));
  }, []);

  const validateName = (value) => {
    (!value || value.length < 1 ) ?
      setValidatedName(ValidatedOptions.error) :
      setValidatedName(ValidatedOptions.default)
  }

  const onNameChange = (value) => {
    setName(value);
    validateName(value);
  };

  const onDescriptionChange = (value) => {
    setDescription(value);
  };

  const validateInventory = (value) => {
    (!value || value.length < 1 ) ?
      setValidatedInventory(ValidatedOptions.error) :
      setValidatedInventory(ValidatedOptions.default)
  };

  const onInventoryChange = (value) => {
    setInventory(value);
    validateInventory(value);
  };


  const validateFields = () => {
    validateName(name);
    validateInventory(inventory);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    validateFields();
    postData(endpoint_inventories, { name: name,
                         inventory: inventory
    })
      .then(() => history.push("/inventories"))
      .catch(() => history.push("/inventories"));
    }

  return (
  <React.Fragment>
    <TopToolbar
      breadcrumbs={[
        {
          title: 'Inventories',
          to: '/inventories'
        },
        {
          title: 'Add'
        }
      ]
      }>
      <Title headingLevel={"h2"}>Add new inventory</Title>
    </TopToolbar>
    <PageSection>
      <Card>
        <CardBody>
          <Form>
            <Grid hasGutter>
              <GridItem span={4}>
                <FormGroup style={{paddingRight: '30px'}}
                           label={intl.formatMessage(sharedMessages.name)}
                           fieldId={`inventory-name`}
                           isRequired
                           helperTextInvalid={ intl.formatMessage(sharedMessages.enterInventoryName) }
                           helperTextInvalidIcon={<ExclamationCircleIcon />}
                           validated={validatedName}
                >
                  <TextInput
                    id="inventory-name"
                    value={name}
                    label="Name"
                    isRequired
                    validated={validatedName}
                    onChange={onNameChange}
                    onBlur={(event) => validateName(name)}
                    placeholder={ intl.formatMessage(sharedMessages.namePlaceholder) }
                  />
                </FormGroup>
              </GridItem>
              <GridItem span={4}>
                <FormGroup style={{paddingRight: '30px'}}
                           label={intl.formatMessage(sharedMessages.description)}
                           fieldId={`inventory-description`}
                           helperTextInvalid={ intl.formatMessage(sharedMessages.enterInventoryDescription) }
                           helperTextInvalidIcon={<ExclamationCircleIcon />}
                >
                  <TextInput
                    id="inventory-description"
                    label="Description"
                    placeholder={ intl.formatMessage(sharedMessages.descriptionPlaceholder) }
                    onChange={onDescriptionChange}
                  />
                </FormGroup>
              </GridItem>
            </Grid>
            <ActionGroup>
              <Button variant="primary" onClick={handleSubmit}>Add</Button>
              <Button variant="link" onClick={() => history.push('/inventories')}> Cancel</Button>
            </ActionGroup>
          </Form>
        </CardBody>
      </Card>
    </PageSection>
  </React.Fragment>
)
}

export { NewInventory };
