import {
  Flex,
  FlexItem,
  Gallery,
  GalleryItem,
  Grid,
  GridItem,
  PageSection,
  Stack,
  StackItem,
  Title
} from '@patternfly/react-core';
import React from 'react';
import { TopToolbar } from '@app/shared/top-toolbar';
import { ProjectsCard } from '@app/Dashboard/ProjectsCard';
import { ActivationsCard } from '@app/Dashboard/ActivationsCard';
import { InventoriesCard } from '@app/Dashboard/InventoriesCard';
import { ActionsCard } from '@app/Dashboard/ActionsCard';

const Dashboard: React.FunctionComponent = () => {
  return (
    <React.Fragment>
      <TopToolbar>
        <Title headingLevel={'h2'}>Dashboard</Title>
      </TopToolbar>
      <PageSection>
        <Stack hasGutter>
          <StackItem>
            <ProjectsCard />
          </StackItem>
          <StackItem>
            <Grid hasGutter>
              <GridItem span={6}>
                <ProjectsCard />
              </GridItem>
              <GridItem span={6}>
                <ActivationsCard />
              </GridItem>
              <GridItem span={6}>
                <InventoriesCard />
              </GridItem>
              <GridItem span={6}>
                <ActionsCard />
              </GridItem>
            </Grid>
          </StackItem>
        </Stack>
      </PageSection>
    </React.Fragment>
  );
};

export { Dashboard };
