import {Title} from '@patternfly/react-core';
import {Route, Switch, useLocation, useParams} from 'react-router-dom';
import React, { useState, useEffect, Fragment } from 'react';
import {useIntl} from "react-intl";
import AppTabs from "@app/shared/app-tabs";
import {CaretLeftIcon} from "@patternfly/react-icons";
import {getServer} from "@app/utils/utils";
import {TopToolbar} from "@app/shared/top-toolbar";
import {ActivationJobs} from "@app/Activation/activation-jobs";
import {ActivationDetails} from "@app/Activation/activation-details";
import {ActivationStdout} from "@app/Activation/activation-stdout";
import {defaultSettings} from "@app/shared/pagination";
import {ActivationType} from "@app/Activations/Activations";
import {JobType} from "@app/Job/Job";
import sharedMessages from "../messages/shared.messages";
import {AnyObject} from "@app/shared/types/common-types";

interface TabItemType {
  eventKey: number;
  title: string;
  name: string;
}
const buildActivationTabs = (activationId: string, intl: AnyObject) : TabItemType[] => ( [
    {
      eventKey: 0,
      title: (
        <div>
          <CaretLeftIcon />
          {intl.formatMessage(sharedMessages.backToRulebookActivations)}
        </div>
      ),
      name: `/activations`
    },
    { eventKey: 1,
      title: 'Details',
      name: `/activation/${activationId}/details` },
    {
      eventKey: 2,
      title: intl.formatMessage(sharedMessages.jobs),
      name: `/activation/${activationId}/jobs`
    },
    {
      eventKey: 3,
      title: intl.formatMessage(sharedMessages.output),
      name: `/activation/${activationId}/stdout`
    }
  ]);

export const renderActivationTabs = (activationId: string, intl) => {
  const activation_tabs = buildActivationTabs(activationId, intl);
  return <AppTabs tabItems={activation_tabs}/>
};

const endpoint1 = 'http://' + getServer() + '/api/activation_instance/';
const endpoint2 = 'http://' + getServer() + '/api/activation_instance_job_instances/';

export const fetchActivationJobs = (activationId, pagination=defaultSettings) =>
{
  return fetch(`${endpoint2}${activationId}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  }).then(response => response.json());
}
export const getTabFromPath = (tabs:TabItemType[], path:string):string | undefined => {
  const currentTab=tabs.find((tabItem) => tabItem.name.split('/').pop() === path.split('/').pop());
  return currentTab?.title;
};

const Activation: React.FunctionComponent = () => {

  const [activation, setActivation] = useState<ActivationType|undefined>(undefined);
  const [websocket_client, setWebsocketClient] = useState<WebSocket|undefined>(undefined);
  const [jobs, setJobs] = useState<JobType[]>([]);
  const [newJob, setNewJob] = useState<JobType|undefined>(undefined);

  const { id } = useParams<{id: string}>();
  const intl = useIntl();

  useEffect(() => {
    fetch(endpoint1 + id, {
      headers: {
        'Content-Type': 'application/json',
      },
    }).then(response => response.json())
      .then(data => setActivation(data));
  }, []);

  useEffect(() => {
    fetchActivationJobs(id)
      .then(data => setJobs(data));
  }, []);

  const [update_client, setUpdateClient] = useState<WebSocket|unknown>({});
  useEffect(() => {
    const uc = new WebSocket('ws://' + getServer() + '/api/ws-activation/' + id);
    setUpdateClient(uc);
    uc.onopen = () => {
      console.log('Update client connected');
    };
    uc.onmessage = (message) => {
      const [messageType, data] = JSON.parse(message.data);
      if (messageType === 'Job') {
        setNewJob(data);
      }
    }
  }, []);

  useEffect(() => {
    if (newJob) {
      setJobs([...jobs, newJob]);
    }
  }, [newJob]);
  const location = useLocation();
  const currentTab = activation?.id ?
    getTabFromPath(buildActivationTabs(activation.id,intl), location.pathname) :
    intl.formatMessage(sharedMessages.details);
  return (
    <React.Fragment>
      <TopToolbar breadcrumbs={[
        {
          title: intl.formatMessage(sharedMessages.rulebookActivations),
          key: 'back-to-activations',
          to: '/activations'
        },
        {
          title: activation?.name,
          key: 'details',
          to: `/activation/${activation?.id}/details`
        },
        {
          title: currentTab || intl.formatMessage(sharedMessages.details),
          key: 'current_tab'
        }
      ]
      }>
        <Title headingLevel={"h2"}>{`${activation?.name}`}</Title>
      </TopToolbar>
      { activation &&
        <Switch>
          <Route exact path="/activation/:id/jobs">
            <ActivationJobs
              jobs={jobs}
              activation={activation}
            />
          </Route>
          <Route exact path="/activation/:id/stdout">
            <ActivationStdout
              activation={activation}
            />
          </Route>
          <Route path="/activation/:id">
            <ActivationDetails
              activation={activation}
            />
          </Route>
        </Switch>
      }
    </React.Fragment>
  );
}

export { Activation };
