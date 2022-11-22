import { Title } from '@patternfly/react-core';
import { Route, Switch, useLocation, useParams } from 'react-router-dom';
import React, { useState, useEffect, ReactNode } from 'react';
import { useIntl } from 'react-intl';
import AppTabs from '@app/shared/app-tabs';
import { CaretLeftIcon } from '@patternfly/react-icons';
import { getTabFromPath } from '@app/utils/utils';
import { TopToolbar } from '@app/shared/top-toolbar';
import { AuditRuleDetails } from '@app/AuditView/audit-rule-details';
import sharedMessages from '../messages/shared.messages';
import { AnyObject } from '@app/shared/types/common-types';
import { fetchAuditRuleDetails } from '@app/API/Audit';
import {AuditRuleJobs} from "@app/AuditView/audit-rule-jobs";
import {AuditRuleHosts} from "@app/AuditView/audit-rule-hosts";
import {RuleType} from "@app/Rules/Rules";
import {AuditRuleEvents} from "@app/AuditView/audit-rule-events";

interface TabItemType {
  eventKey: number;
  title: string | ReactNode;
  name: string;
}

const buildAuditRuleTabs = (ruleId: string, intl: AnyObject): TabItemType[] => [
  {
    eventKey: 0,
    title: (
      <div>
        <CaretLeftIcon />
        {intl.formatMessage(sharedMessages.backToAuditView)}
      </div>
    ),
    name: `/audit`,
  },
  { eventKey: 1, title: 'Details', name: `/audit-rule/${ruleId}/details` },
  { eventKey: 2, title: 'Jobs', name: `/audit-rule/${ruleId}/jobs` },
  { eventKey: 3, title: 'Hosts', name: `/audit-rule/${ruleId}/hosts` },
  { eventKey: 4, title: 'Events', name: `/audit-rule/${ruleId}/events` },
];

export const renderAuditRuleTabs = (ruleId: string, intl) => {
  const rule_tabs = buildAuditRuleTabs(ruleId, intl);
  return <AppTabs tabItems={rule_tabs} />;
};

const AuditRule: React.FunctionComponent = () => {
  const [rule, setRule] = useState<RuleType | undefined>(undefined);

  const { id } = useParams<{ id: string }>();
  const intl = useIntl();

  useEffect(() => {
    fetchAuditRuleDetails(id).then((data) => setRule(data?.data));
  }, []);

  const location = useLocation();
  const currentTab = rule?.id
    ? getTabFromPath(buildAuditRuleTabs(rule.id, intl), location.pathname)
    : intl.formatMessage(sharedMessages.details);
  console.log('Debug - rule, location.pathname, currentTab', rule, location.pathname, currentTab);
  return (
    <React.Fragment>
      <TopToolbar
        breadcrumbs={[
          {
            title: intl.formatMessage(sharedMessages.audit_view_title),
            key: 'audit-view',
            to: '/audit',
          },
          {
            title: rule?.name || '',
            key: 'details',
            to: `/audit-rule/${rule?.id}`,
          },
          {
            title: currentTab || intl.formatMessage(sharedMessages.details),
            key: 'current_tab',
          },
        ]}
      >
        <Title headingLevel={'h2'}>{`${rule?.name}`}</Title>
      </TopToolbar>
      {rule && (
        <Switch>
          <Route exact path="/audit-rule/:id/jobs">
            <AuditRuleJobs rule={rule} />
          </Route>
          <Route exact path="/audit-rule/:id/hosts">
            <AuditRuleHosts rule={rule} />
          </Route>
          <Route exact path="/audit-rule/:id/events">
            <AuditRuleEvents rule={rule} />
          </Route>
          <Route path="/audit-rule/:id">
            <AuditRuleDetails rule={rule} />
          </Route>
        </Switch>
      )}
    </React.Fragment>
  );
};

export { AuditRule };
