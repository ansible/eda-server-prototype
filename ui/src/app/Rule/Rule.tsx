import {Title} from '@patternfly/react-core';
import {Route, Switch, useLocation, useParams} from 'react-router-dom';
import React, {useState, useEffect, ReactNode} from 'react';
import {useIntl} from "react-intl";
import AppTabs from "@app/shared/app-tabs";
import {CaretLeftIcon} from "@patternfly/react-icons";
import {getServer, getTabFromPath} from "@app/utils/utils";
import {TopToolbar} from "@app/shared/top-toolbar";
import {RuleDetails} from "@app/Rule/rule-details";
import {defaultSettings} from "@app/shared/pagination";
import {RuleType} from "@app/Rules/Rules";
import sharedMessages from "../messages/shared.messages";
import {AnyObject} from "@app/shared/types/common-types";

interface TabItemType {
  eventKey: number;
  title: string | ReactNode;
  name: string;
}
const buildRuleTabs = (ruleId: string, intl: AnyObject) : TabItemType[] => ( [
    {
      eventKey: 0,
      title: (
        <div>
          <CaretLeftIcon />
          {intl.formatMessage(sharedMessages.backToRules)}
        </div>
      ),
      name: `/rules`
    },
    { eventKey: 1,
      title: 'Details',
      name: `/rule/${ruleId}/details` }
  ]);

export const renderRuleTabs = (ruleId: string, intl) => {
  const rule_tabs = buildRuleTabs(ruleId, intl);
  return <AppTabs tabItems={rule_tabs}/>
};

const endpoint_rule = 'http://' + getServer() + '/api/rules/';

export const fetchRule = (ruleId, pagination=defaultSettings) =>
{
  return fetch(`${endpoint_rule}${ruleId}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then(response => response.json());
}

const Rule: React.FunctionComponent = () => {

  const [rule, setRule] = useState<RuleType|undefined>(undefined);

  const { id } = useParams<{id: string}>();
  const intl = useIntl();

  useEffect(() => {
   fetchRule(id)
      .then(data => setRule(data));
  }, []);

  const location = useLocation();
  const currentTab = rule?.id ?
    getTabFromPath(buildRuleTabs(rule.id,intl), location.pathname) :
    intl.formatMessage(sharedMessages.details);
  return (
    <React.Fragment>
      <TopToolbar breadcrumbs={[
        {
          title: intl.formatMessage(sharedMessages.rules),
          key: 'back-to-rules',
          to: '/rules'
        },
        {
          title: rule?.name || '',
          key: 'details',
          to: `/rule/${rule?.id}`
        },
        {
          title: currentTab || intl.formatMessage(sharedMessages.details),
          key: 'current_tab'
        }
      ]
      }>
        <Title headingLevel={"h2"}>{`${rule?.name}`}</Title>
      </TopToolbar>
      { rule &&
        <Switch>
          <Route path="/rule/:id">
            <RuleDetails
              rule={rule}
            />
          </Route>
        </Switch>
      }
    </React.Fragment>
  );
}

export { Rule };
