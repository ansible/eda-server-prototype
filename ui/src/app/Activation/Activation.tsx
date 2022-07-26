import {Card, CardBody, PageSection, Tab, Tabs, Title} from '@patternfly/react-core';
import { Link, Route, Switch, useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import AppTabs from "@app/shared/app-tabs";

import {CaretLeftIcon} from "@patternfly/react-icons";

export const renderActivationTabs = (activationId: string) => {
  const activation_tabs = [
    {
      eventKey: 0,
      title: (
        <>
          <CaretLeftIcon />
          {'Back to Activations'}
        </>
      ),
      name: `/activations`,
    },
    { eventKey: 1, title: 'Details', name: `/activation/${activationId}/details` },
    {
      eventKey: 2,
      title: 'Jobs',
      name: `/activation/${activationId}/jobs`,
    }
  ];

  return <AppTabs tabItems={activation_tabs}/>
};

