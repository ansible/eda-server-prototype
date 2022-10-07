import {Title} from '@patternfly/react-core';
import {Route, Switch, useLocation, useParams} from 'react-router-dom';
import React, { useState, useEffect, Fragment } from 'react';
import {useIntl} from "react-intl";
import AppTabs from "@app/shared/app-tabs";
import {CaretLeftIcon} from "@patternfly/react-icons";
import {getServer, getTabFromPath} from "@app/utils/utils";
import {TopToolbar} from "@app/shared/top-toolbar";
import {RulesetRules} from "@app/RuleSet/ruleset-rules";
import {RulesetDetails} from "@app/RuleSet/ruleset-details";
import {RulesetSources} from "@app/RuleSet/ruleset-sources";
import sharedMessages from "../messages/shared.messages";
import {AnyObject} from "@app/shared/types/common-types";

interface TabItemType {
  eventKey: number;
  title: string;
  name: string;
}

export interface RuleSetType {
  id: string,
  name?: string,
  description?: string,
  project?: { id: string, name: string },
  rulebook?: { id: string, name: string },
  rule_count?: string,
  created_at?: string,
  modified_at?: string
}

export interface RuleType {
  id: string,
  name: string,
  fire_count: number,
  list_fired_date: string
}

const buildRuleSetFileTabs = (rulesetId: string, intl: AnyObject) : TabItemType[] => ( [
    {
      eventKey: 0,
      title: (
        <div>
          <CaretLeftIcon/>
          {intl.formatMessage(sharedMessages.backToRuleSets)}
        </div>
      ),
      name: `/rulesets`
    },
    { eventKey: 1,
      title: 'Details',
      name: `/ruleset/${rulesetId}/details` },
    {
      eventKey: 2,
      title: intl.formatMessage(sharedMessages.rules),
      name: `/ruleset/${rulesetId}/rules`
    },
    {
      eventKey: 3,
      title: intl.formatMessage(sharedMessages.sources),
      name: `/ruleset/${rulesetId}/sources`
    }
  ]);

export const renderRuleSetFileTabs = (rulesetId: string, intl) => {
  const ruleset_tabs = buildRuleSetFileTabs(rulesetId, intl);
  return <AppTabs tabItems={ruleset_tabs}/>
};

const endpoint_ruleset = 'http://' + getServer() + '/api/rulesets/';
const endpoint_rulebook_json = 'http://' + getServer() + '/api/rulebook_json/';

const RuleSet: React.FunctionComponent = () => {
  const [ruleset, setRuleSet] = useState<RuleSetType|undefined>(undefined);
  const { id } = useParams<{id: string}>();
  const intl = useIntl();

  useEffect(() => {
    fetch(`${endpoint_ruleset}${id}`, {
      headers: {
        'Content-Type': 'application/json',
      },
    }).then(response => response.json())
      .then(data => setRuleSet(data));
  }, []);

  const location = useLocation();
  const currentTab = ruleset?.id ?
    getTabFromPath(buildRuleSetFileTabs(ruleset.id,intl), location.pathname) :
    intl.formatMessage(sharedMessages.details);
  return (
    <React.Fragment>
      <TopToolbar breadcrumbs={[
        {
          title: intl.formatMessage(sharedMessages.rulesets),
          key: 'rulesets',
          to: '/rulesets'
        },
        {
          title: ruleset?.name,
          key: 'details',
          to: `/ruleset/${ruleset?.id}/details`
        },
        {
          title: currentTab || intl.formatMessage(sharedMessages.details),
          key: 'current_tab'
        }
      ]
      }>
        <Title headingLevel={"h2"}>{`${ruleset?.name}`}</Title>
      </TopToolbar>
      { ruleset &&
        <Switch>
          <Route exact path="/ruleset/:id/rules">
            <RulesetRules
              ruleset={ruleset}
            />
          </Route>
          <Route exact path="/ruleset/:id/sources">
            <RulesetSources
              ruleset={ruleset}
            />
          </Route>
          <Route path="/ruleset/:id">
            <RulesetDetails
              ruleset={ruleset}
            />
          </Route>
        </Switch>
      }
    </React.Fragment>
  );
}

export { RuleSet};
