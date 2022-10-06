import {
  ActionGroup,
  Button,
  Card,
  CardBody as PFCardBody,
  Form,
  FormGroup,
  Grid, GridItem,
  PageSection,
  Stack,
  StackItem,
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
import AceEditor from "react-ace";
import {FocusWrapper} from "@app/Activation/activation-details";
import 'ace-builds/src-noconflict/theme-kuroir';

const CardBody = styled(PFCardBody)`
  white-space: pre-wrap;
  `
const endpoint_inventories = 'http://' + getServer() + '/api/inventories/';

const NewInventory: React.FunctionComponent = () => {
  const history = useHistory();
  const intl = useIntl();
    const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [inventory, setInventory] = useState('');

  const [ validatedName, setValidatedName ] = useState<ValidatedOptions>(ValidatedOptions.default);
  const [ validatedInventory, setValidatedInventory ] = useState<ValidatedOptions>(ValidatedOptions.default);

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
            <Stack hasGutter>
              <StackItem>
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
              </StackItem>
              <StackItem>
                <FormGroup label={intl.formatMessage(sharedMessages.inventory)}
                           fieldId={`inventory-inventory`}
                >
                  <Card>
                    <FocusWrapper>
                      <AceEditor
                        theme={"kuroir"}
                        name="inventory_inventory"
                        fontSize={16}
                        value={inventory}
                        height={'200px'}
                        width={'100pct'}
                        setOptions={{
                          enableBasicAutocompletion: false,
                          enableLiveAutocompletion: false,
                          enableSnippets: false,
                          showLineNumbers: true,
                          tabSize: 2,
                          focus: false,
                          highlightActiveLine: false,
                          cursorStart: 0,
                          cursorStyle: undefined
                        }}/>
                    </FocusWrapper>
                  </Card>
                </FormGroup>
              </StackItem>
              <StackItem>
                <ActionGroup>
                  <Button variant="primary" isDisabled={true} onClick={handleSubmit}>Add</Button>
                  <Button variant="link" onClick={() => history.push('/inventories')}> Cancel</Button>
                </ActionGroup>
              </StackItem>
            </Stack>
          </Form>
        </CardBody>
      </Card>
    </PageSection>
  </React.Fragment>
)
}

export { NewInventory };
