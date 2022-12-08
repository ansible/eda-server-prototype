import React from 'react';
import { Level, LevelItem, Title } from '@patternfly/react-core';
import { Route, Switch, useLocation } from 'react-router-dom';
import { useIntl } from 'react-intl';
import AppTabs from '@app/shared/app-tabs';
import { TopToolbar } from '@app/shared/top-toolbar';
import { AnyObject, TabItemType } from '@app/shared/types/common-types';
import sharedMessages from '../messages/shared.messages';
import { ActionsRules } from '@app/Actions/actions-rules';
import { ActionsHosts } from '@app/Actions/actions-hosts';

export interface ActionsRuleType {
  id: string;
  name: string;
  job: string;
  job_name: string;
  status: string;
  ruleset: string;
  ruleset_name: string;
  fired_at?: string;
}

export interface ActionsHostType {
  rule: { id: string; name: string };
  job?: { id: string; name: string };
  ruleset?: { id: string; name: string };
  status: string;
  fired_date?: string;
}

const buildActionsTabs = (intl: AnyObject): TabItemType[] => [
  { eventKey: 0, title: intl.formatMessage(sharedMessages.actions_title), name: `/actions/rules` },
  {
    eventKey: 1,
    title: intl.formatMessage(sharedMessages.actions_hosts_title),
    name: `/actions/hosts`,
  },
];

export const renderActionsTabs = (intl) => {
  const actions_tabs = buildActionsTabs(intl);
  return <AppTabs tabItems={actions_tabs} defaultActive={0} />;
};

const Actions: React.FunctionComponent = () => {
  const intl = useIntl();

  return (
    <React.Fragment>
      <TopToolbar>
        <Level>
          <LevelItem>
            <Title headingLevel={'h2'}>{intl.formatMessage(sharedMessages.actions_view_title)}</Title>
          </LevelItem>
        </Level>
      </TopToolbar>
      <Switch>
        <Route exact path="/actions/hosts">
          <ActionsHosts />
        </Route>
        <Route path="/actions">
          <ActionsRules />
        </Route>
      </Switch>
    </React.Fragment>
  );
};

export { Actions };
