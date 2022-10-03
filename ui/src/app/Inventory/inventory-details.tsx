import {
  Card,
  CardBody,
  Flex,
  FlexItem,
  PageSection,
  Stack,
  StackItem,
  Title
} from '@patternfly/react-core';
import {useParams} from 'react-router-dom';
import React from 'react';
import {renderInventoryTabs, InventoryType} from "@app/Inventory/inventory";
import {useIntl} from "react-intl";
import sharedMessages from "../messages/shared.messages";

const InventoryDetails: React.FunctionComponent<{inventory: InventoryType}> = ({ inventory }) => {
  const intl = useIntl();
  const {id} = useParams<{id: string}>();

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
                <StackItem><Title headingLevel="h3">{intl.formatMessage(sharedMessages.inventory)}</Title></StackItem>
                <StackItem>
                  { inventory?.inventory }
                </StackItem>
              </Stack>
            </FlexItem>
          </Flex>
        </Flex>
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
