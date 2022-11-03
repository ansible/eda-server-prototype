import { Title } from '@patternfly/react-core';
import React from 'react';
import { TopToolbar } from '@app/shared/top-toolbar';

const NewRuleSet: React.FunctionComponent = () => {
  return (
    <React.Fragment>
      <TopToolbar>
        <Title headingLevel={'h2'}>New Rule Set</Title>
      </TopToolbar>
    </React.Fragment>
  );
};

export { NewRuleSet };
