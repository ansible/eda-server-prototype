import { Title } from '@patternfly/react-core';
import React from 'react';
import { TopToolbar } from '@app/shared/top-toolbar';

const AuditView: React.FunctionComponent = () => {
  return (
    <React.Fragment>
      <TopToolbar>
        <Title headingLevel={'h2'}>Audit View</Title>
      </TopToolbar>
    </React.Fragment>
  );
};

export { AuditView };
