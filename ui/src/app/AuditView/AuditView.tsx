import React from 'react';
import { Level, LevelItem, Title } from '@patternfly/react-core';
import { Route, Switch, useLocation } from 'react-router-dom';
import { useIntl } from 'react-intl';
import AppTabs from '@app/shared/app-tabs';
import { TopToolbar } from '@app/shared/top-toolbar';
import { AnyObject, TabItemType } from '@app/shared/types/common-types';
import sharedMessages from '../messages/shared.messages';
import {AuditRules} from "@app/AuditView/audit-rules";
import {AuditHosts} from "@app/AuditView/audit-hosts";

export interface AuditRuleType {
  id: string;
  name: string;
  job: string;
  job_name: string;
  status: string;
  ruleset: string;
  ruleset_name: string;
  fired_at?: string;
}

export interface AuditHostType {
  name: string;
  rule: string;
  rule_name: string;
  status: string;
  ruleset: string;
  ruleset_name: string;
  fired_at?: string;
}

const buildAuditTabs = (intl: AnyObject): TabItemType[] => [
  { eventKey: 0, title: intl.formatMessage(sharedMessages.audit_rules_title), name: `/audit/rules` },
  {
    eventKey: 1,
    title: intl.formatMessage(sharedMessages.audit_hosts_title),
    name: `/audit/hosts`,
  },
];

export const renderAuditTabs = (intl) => {
  const audit_tabs = buildAuditTabs(intl);
  return <AppTabs tabItems={audit_tabs} defaultActive={0} />;
};

const AuditView: React.FunctionComponent = () => {
  const intl = useIntl();

  return (
    <React.Fragment>
      <TopToolbar>
        <Level>
          <LevelItem>
            <Title headingLevel={'h2'}>{intl.formatMessage(sharedMessages.audit_view_title)}</Title>
          </LevelItem>
        </Level>
      </TopToolbar>
      <Switch>
        <Route exact path="/audit/hosts">
          <AuditHosts/>
        </Route>
        <Route path="/audit">
          <AuditRules/>
        </Route>
      </Switch>
    </React.Fragment>
  );
};

export { AuditView };
