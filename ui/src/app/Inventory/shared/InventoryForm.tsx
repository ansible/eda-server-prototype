import {
  ActionGroup,
  Button,
  FormGroup,
  Grid,
  GridItem,
  Stack,
  StackItem,
  TextInput,
  ValidatedOptions,
} from '@patternfly/react-core';
import { useHistory } from 'react-router-dom';
import React, { useState } from 'react';
import { ExclamationCircleIcon } from '@patternfly/react-icons';
import { useIntl } from 'react-intl';
import sharedMessages from '../../messages/shared.messages';
import { InventoryType } from '../inventory';
import { EdaCodeEditor } from '@app/utils/EdaCodeEditor';
import { Language } from '@patternfly/react-code-editor';

function InventoryForm(props: {
  inventory?: InventoryType;
  handleSubmit: (name: string, inventory: string, description?: string | undefined) => void;
  isSubmitting: boolean;
}): JSX.Element {
  const { inventory, isSubmitting, handleSubmit } = props;
  const history = useHistory();
  const intl = useIntl();
  const [validatedName, setValidatedName] = useState<ValidatedOptions>(ValidatedOptions.default);

  const validateName = (value: string) => {
    !value || value.length < 1 ? setValidatedName(ValidatedOptions.error) : setValidatedName(ValidatedOptions.default);
  };
  const [name, setName] = useState(inventory?.name || '');
  const [inventoryVars, setInventoryVars] = useState(inventory?.inventory || '');
  const [description, setDescription] = useState(inventory?.description || '');
  return (
    <>
      <Stack hasGutter>
        <StackItem>
          <Grid hasGutter>
            <GridItem span={4}>
              <FormGroup
                style={{ paddingRight: '30px' }}
                label={intl.formatMessage(sharedMessages.name)}
                fieldId={`inventory-name`}
                isRequired
                helperTextInvalid={intl.formatMessage(sharedMessages.enterInventoryName)}
                helperTextInvalidIcon={<ExclamationCircleIcon />}
                validated={validatedName}
              >
                <TextInput
                  id="inventory-name"
                  value={name}
                  label="Name"
                  isRequired
                  validated={validatedName}
                  onChange={(v) => setName(v)}
                  onBlur={(event) => validateName(name)}
                  placeholder={intl.formatMessage(sharedMessages.namePlaceholder)}
                />
              </FormGroup>
            </GridItem>
            <GridItem span={4}>
              <FormGroup
                style={{ paddingRight: '30px' }}
                label={intl.formatMessage(sharedMessages.description)}
                fieldId={`inventory-description`}
                helperTextInvalid={intl.formatMessage(sharedMessages.enterInventoryDescription)}
                helperTextInvalidIcon={<ExclamationCircleIcon />}
              >
                <TextInput
                  id="inventory-description"
                  label="Description"
                  value={description}
                  placeholder={intl.formatMessage(sharedMessages.descriptionPlaceholder)}
                  onChange={(v) => setDescription(v)}
                />
              </FormGroup>
            </GridItem>
          </Grid>
        </StackItem>
        <StackItem>
          <FormGroup isRequired label={intl.formatMessage(sharedMessages.inventory)} fieldId={`inventory-inventory`}>
            <EdaCodeEditor
              code={inventoryVars}
              editMode={true}
              setEditedCode={setInventoryVars}
              language={Language.yaml}
              width={'100%'}
              height={'400'}
            />
          </FormGroup>
        </StackItem>
        <StackItem>
          <ActionGroup>
            <Button
              variant="primary"
              onClick={() => handleSubmit(name, inventoryVars, description)}
              isLoading={isSubmitting}
            >
              {isSubmitting ? 'Saving ' : 'Save'}
            </Button>
            <Button variant="link" onClick={() => history.push('/inventories')}>
              Cancel
            </Button>
          </ActionGroup>
        </StackItem>
      </Stack>
    </>
  );
}
export default InventoryForm;
