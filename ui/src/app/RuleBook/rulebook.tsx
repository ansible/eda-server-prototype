import {Title} from '@patternfly/react-core';
import {Route, Switch, useLocation, useParams} from 'react-router-dom';
import React, { useState, useEffect, Fragment } from 'react';
import {useIntl} from "react-intl";
import AppTabs from "@app/shared/app-tabs";
import {CaretLeftIcon} from "@patternfly/react-icons";
import {getServer, getTabFromPath} from "@app/utils/utils";
import {TopToolbar} from "@app/shared/top-toolbar";
import {RulebookRulesets} from "@app/RuleBook/rulebook-rulesets";
import {RulebookDetails} from "@app/RuleBook/rulebook-details";
import sharedMessages from "../messages/shared.messages";
import {AnyObject, TabItemType} from "@app/shared/types/common-types";

export interface RuleBookType {
  id: string,
  name?: string,
  description?: string,
  number_of_rulesets?: string,
  created_at?: string,
  fire_count?: string,
  last_modified?: string
}

export interface RuleSetType {
  id: string,
  name: string,
  fire_count: number,
  list_fired_date: string
}

const buildRuleBookTabs = (rulebookId: string, intl: AnyObject) : TabItemType[] => ( [
    {
      eventKey: 0,
      title: (
        <div>
          <CaretLeftIcon/>
          {intl.formatMessage(sharedMessages.backToRuleBooks)}
        </div>
      ),
      name: `/rulebooks`
    },
    { eventKey: 1,
      title: 'Details',
      name: `/rulebooks/rulebook/${rulebookId}/details` },
    {
      eventKey: 2,
      title: intl.formatMessage(sharedMessages.rulesets),
      name: `/rulebooks/rulebook/${rulebookId}/rulesets`
    }
  ]);

export const renderRuleBookTabs = (rulebookId: string, intl) => {
  const rulebook_tabs = buildRuleBookTabs(rulebookId, intl);
  return <AppTabs tabItems={rulebook_tabs}/>
};

const endpoint_rulebook = 'http://' + getServer() + '/api/rulebooks/';

const RuleBook: React.FunctionComponent = () => {
  const [rulebook, setRuleBook] = useState<RuleBookType|undefined>(undefined);
  const { id } = useParams<{id: string}>();
  const intl = useIntl();

  useEffect(() => {
    fetch(`${endpoint_rulebook}${id}`, {
      headers: {
        'Content-Type': 'application/json',
      },
    }).then(response => response.json())
      .then(data => setRuleBook(data));
  }, []);

  const location = useLocation();
  const currentTab = rulebook?.id ?
    getTabFromPath(buildRuleBookTabs(rulebook.id,intl), location.pathname) :
    intl.formatMessage(sharedMessages.details);
  return (
    <React.Fragment>
      <TopToolbar breadcrumbs={[
        {
          title: intl.formatMessage(sharedMessages.rulebooks),
          key: 'rulebooks',
          to: '/rulebooks'
        },
        {
          title: rulebook?.name,
          key: 'details',
          to: `/rulebooks/rulebook/${rulebook?.id}/details`
        },
        {
          title: currentTab || intl.formatMessage(sharedMessages.details),
          key: 'current_tab'
        }
      ]
      }>
        <Title headingLevel={"h2"}>{`${rulebook?.name}`}</Title>
      </TopToolbar>
      { rulebook &&
        <Switch>
          <Route exact path="/rulebooks/rulebook/:id/rulesets">
            <RulebookRulesets
              rulebook={rulebook}
            />
          </Route>
          <Route path="/rulebooks/rulebook/:id">
            <RulebookDetails
              rulebook={rulebook}
            />
          </Route>
        </Switch>
      }
    </React.Fragment>
  );
}

export { RuleBook};
