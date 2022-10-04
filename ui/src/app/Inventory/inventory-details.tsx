import {
  Card,
  CardBody,
  Flex,
  FlexItem, Grid, GridItem,
  PageSection,
  Stack,
  StackItem,
  Title, ToggleGroup, ToggleGroupItem
} from '@patternfly/react-core';
import {useParams} from 'react-router-dom';
import React, {useState} from 'react';
import {renderInventoryTabs, InventoryType} from "@app/Inventory/inventory";
import {useIntl} from "react-intl";
import sharedMessages from "../messages/shared.messages";
import ReactJsonView from "react-json-view";
import AceEditor from "react-ace";
import {FocusWrapper} from "@app/Activation/activation-details";
import 'ace-builds/src-noconflict/theme-kuroir';

const InventoryDetails: React.FunctionComponent<{inventory: InventoryType}> = ({ inventory }) => {
  const intl = useIntl();
  const {id} = useParams<{id: string}>();
  const [invFormat, setInvFormat] = useState('yaml');

  const handleToggleFormat = (_, event) => {
    const id = event.currentTarget.id;
    setInvFormat(id );
  }
  const renderFlexInventoryDetails: React.FunctionComponent<InventoryType> = (inventory) => (
    <Stack hasGutter={true}>
      <StackItem>
        <Flex>
          <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.name)}</Title></StackItem>
                <StackItem>
                  {inventory?.name}
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.created)}</Title></StackItem>
                <StackItem>
                  {inventory?.created_at}
                </StackItem>
              </Stack>
            </FlexItem>
          </Flex>
          <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.description)}</Title></StackItem>
                <StackItem>
                  {inventory?.description}
                </StackItem>
              </Stack>
            </FlexItem>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.lastModified)}</Title></StackItem>
                <StackItem>
                  {inventory?.modified_at}
                </StackItem>
              </Stack>
            </FlexItem>
          </Flex>
          <Flex direction={{ default: 'column' }} flex={{ default: 'flex_1' }}>
            <FlexItem>
              <Stack>
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.source_of_inventory)}</Title></StackItem>
                <StackItem>
                  { inventory?.source }
                </StackItem>
              </Stack>
            </FlexItem>
          </Flex>
        </Flex>
      </StackItem>
      <StackItem>
        <Stack hasGutter={true}>
          <StackItem>
            <Grid>
              <GridItem span={1}>
                <Title headingLevel="h3">Variables</Title>
              </GridItem>
              <GridItem span={2}>
                <ToggleGroup isCompact aria-label="JsonYaml">
                  <ToggleGroupItem text="YAML" buttonId="yaml" isSelected={invFormat === 'yaml' } onChange={handleToggleFormat} />
                  <ToggleGroupItem text="JSON" buttonId="json" isSelected={invFormat === 'json'} onChange={handleToggleFormat} />
                </ToggleGroup>
              </GridItem>
            </Grid>
          </StackItem>
          <StackItem>
            {inventory?.inventory ? ( invFormat === 'json' ?
                <ReactJsonView displayObjectSize={false}
                               displayDataTypes={false}
                               quotesOnKeys={false}
                               src={{inventory: inventory.inventory}}/> :
                <Card>
                  <FocusWrapper>
                    <AceEditor
                      theme={"kuroir"}
                      name="inventory_inventory"
                      fontSize={16}
                      value={inventory?.inventory}
                      height={'200px'}
                      width={'100pct'}
                      setOptions={{
                        enableBasicAutocompletion: false,
                        enableLiveAutocompletion: false,
                        enableSnippets: false,
                        showLineNumbers: true,
                        tabSize: 2,
                        readOnly: true,
                        focus: false,
                        highlightActiveLine: false,
                        cursorStart: 0,
                        cursorStyle: undefined
                      }}/>
                  </FocusWrapper>
                </Card>
            ) : null
            }
          </StackItem>
        </Stack>
      </StackItem>
     </Stack>
  );

  return (
  <PageSection page-type={'inventory-details'} id={'inventory-details'}>
    { renderInventoryTabs(id, intl) }
    <Stack>
      <StackItem>
        <Card>
          <CardBody>
            {renderFlexInventoryDetails(inventory)}
          </CardBody>
        </Card>
      </StackItem>
    </Stack>
  </PageSection>
)
}

export { InventoryDetails };
