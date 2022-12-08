import { Skeleton, Title } from '@patternfly/react-core';
import { Route, Switch, useLocation, useParams } from 'react-router-dom';
import React, { useState, useEffect, ReactNode } from 'react';
import { useIntl } from 'react-intl';
import AppTabs from '@app/shared/app-tabs';
import { CaretLeftIcon } from '@patternfly/react-icons';
import { getTabFromPath } from '@app/utils/utils';
import { TopToolbar } from '@app/shared/top-toolbar';
import { ActionsRuleDetails } from '@app/Actions/actions-rule-details';
import sharedMessages from '../messages/shared.messages';
import { AnyObject } from '@app/shared/types/common-types';
import { fetchActionsRuleDetails } from '@app/API/Actions';
import { ActionsRuleJobs } from '@app/Actions/actions-rule-jobs';
import { ActionsRuleHosts } from '@app/Actions/actions-rule-hosts';
import { RuleType } from '@app/Rules/Rules';
import { ActionsRuleEvents } from '@app/Actions/actions-rule-events';

interface TabItemType {
  eventKey: number;
  title: string | ReactNode;
  name: string;
}

const buildActionsRuleTabs = (ruleId: string, intl: AnyObject): TabItemType[] => [
  {
    eventKey: 0,
    title: (
      <div>
        <CaretLeftIcon />
        {intl.formatMessage(sharedMessages.backToActions)}
      </div>
    ),
    name: `/actions`,
  },
  { eventKey: 1, title: 'Details', name: `/actions-rule/${ruleId}/details` },
  { eventKey: 2, title: 'Jobs', name: `/actions-rule/${ruleId}/jobs` },
  { eventKey: 3, title: 'Hosts', name: `/actions-rule/${ruleId}/hosts` },
  { eventKey: 4, title: 'Events', name: `/actions-rule/${ruleId}/events` },
];

export const renderActionsRuleTabs = (ruleId: string, intl) => {
  const rule_tabs = buildActionsRuleTabs(ruleId, intl);
  return <AppTabs tabItems={rule_tabs} />;
};

const ActionsRule: React.FunctionComponent = () => {
  const [rule, setRule] = useState<RuleType | undefined>(undefined);

  const { id } = useParams<{ id: string }>();
  const intl = useIntl();

  useEffect(() => {
    fetchActionsRuleDetails(id).then((data) => {
      return setRule(data?.data);
    });
  }, [id]);
  const location = useLocation();
  const currentTab = id
    ? getTabFromPath(buildActionsRuleTabs(id, intl), location.pathname)
    : intl.formatMessage(sharedMessages.details);

  return rule ? (
    <React.Fragment>
      <TopToolbar
        breadcrumbs={[
          {
            title: intl.formatMessage(sharedMessages.actions_view_title),
            key: 'actions-view',
            to: '/actions',
          },
          {
            title: rule?.name || '',
            key: 'details',
            to: `/actions-rule/${id}`,
          },
          {
            title: currentTab || intl.formatMessage(sharedMessages.details),
            key: 'current_tab',
          },
        ]}
      >
        <Title headingLevel={'h2'}>{`${rule?.name}`}</Title>
      </TopToolbar>
      <Switch>
        <Route exact path="/actions-rule/:id/jobs">
          <ActionsRuleJobs rule={rule} />
        </Route>
        <Route exact path="/actions-rule/:id/hosts">
          <ActionsRuleHosts rule={rule} />
        </Route>
        <Route exact path="/actions-rule/:id/events">
          <ActionsRuleEvents rule={rule} />
        </Route>
        <Route path="/actions-rule/:id">
          <ActionsRuleDetails rule={rule} />
        </Route>
      </Switch>
    </React.Fragment>
  ) : (
    <Skeleton />
  );
};

export { ActionsRule };
