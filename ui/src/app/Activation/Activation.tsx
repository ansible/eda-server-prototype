import { Dropdown, DropdownItem, DropdownPosition, KebabToggle, Level, LevelItem, Title } from '@patternfly/react-core';
import { Link, Route, Switch, useLocation, useParams } from 'react-router-dom';
import React, { useState, useEffect, Fragment } from 'react';
import { useIntl } from 'react-intl';
import AppTabs from '@app/shared/app-tabs';
import { CaretLeftIcon } from '@patternfly/react-icons';
import { getServer, getTabFromPath } from '@app/utils/utils';
import { TopToolbar } from '@app/shared/top-toolbar';
import { ActivationJobs } from '@app/Activation/activation-jobs';
import { ActivationDetails } from '@app/Activation/activation-details';
import { ActivationStdout } from '@app/Activation/activation-stdout';
import { ActivationType } from '@app/Activations/Activations';
import { JobType } from '@app/Job/Job';
import { AnyObject, TabItemType } from '@app/shared/types/common-types';
import sharedMessages from '../messages/shared.messages';
import { RemoveActivation } from '@app/RemoveActivation/RemoveActivation';
import { fetchActivation, listActivationJobs } from '@app/API/Activation';

const buildActivationTabs = (activationId: string, intl: AnyObject): TabItemType[] => [
  {
    eventKey: 0,
    title: (
      <div>
        <CaretLeftIcon />
        {intl.formatMessage(sharedMessages.backToRulebookActivations)}
      </div>
    ),
    name: `/activations`,
  },
  { eventKey: 1, title: 'Details', name: `/activation/${activationId}/details` },
  {
    eventKey: 2,
    title: intl.formatMessage(sharedMessages.jobs),
    name: `/activation/${activationId}/jobs`,
  },
  {
    eventKey: 3,
    title: intl.formatMessage(sharedMessages.output),
    name: `/activation/${activationId}/stdout`,
  },
];

export const renderActivationTabs = (activationId: string, intl) => {
  const activation_tabs = buildActivationTabs(activationId, intl);
  return <AppTabs tabItems={activation_tabs} />;
};

const Activation: React.FunctionComponent = () => {
  const [activation, setActivation] = useState<ActivationType | undefined>(undefined);
  const [websocket_client, setWebsocketClient] = useState<WebSocket | undefined>(undefined);
  const [jobs, setJobs] = useState<JobType[]>([]);
  const [newJob, setNewJob] = useState<JobType | undefined>(undefined);
  const [isOpen, setOpen] = useState<boolean>(false);
  const { id } = useParams<{ id: string }>();
  const intl = useIntl();

  useEffect(() => {
    fetchActivation(id).then((data) => setActivation(data));
  }, []);

  useEffect(() => {
    listActivationJobs(id).then((data) => setJobs(data));
  }, []);

  const [update_client, setUpdateClient] = useState<WebSocket | unknown>({});
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
    };
  }, []);

  useEffect(() => {
    if (newJob) {
      setJobs([...jobs, newJob]);
    }
  }, [newJob]);

  const dropdownItems = [
    <DropdownItem
      aria-label="Edit"
      key="relaunch-activation"
      id="relaunch-activation"
      component={<Link to={`/activation/${id}/relaunch`}>{intl.formatMessage(sharedMessages.relaunch)}</Link>}
      role="link"
    />,
    <DropdownItem
      aria-label="Restart"
      key="restart-activation"
      id="restart-activation"
      component={<Link to={`/activation/${id}/restart`}>{intl.formatMessage(sharedMessages.restart)}</Link>}
      role="link"
    />,
    <DropdownItem
      aria-label="Disable"
      key="disable-activation"
      id="disable-activation"
      component={<Link to={`/activation/${id}/disable`}>{intl.formatMessage(sharedMessages.disable)}</Link>}
      role="link"
    />,
    <DropdownItem
      aria-label="Delete"
      key="delete-activation"
      id="delete-activation"
      component={<Link to={`/activation/${id}/remove`}>{intl.formatMessage(sharedMessages.delete)}</Link>}
      role="link"
    />,
  ];

  const routes = () => (
    <Fragment>
      <Route exact path="/activation/:id/remove" render={(props: AnyObject) => <RemoveActivation {...props} />} />
    </Fragment>
  );

  const location = useLocation();
  const currentTab = activation?.id
    ? getTabFromPath(buildActivationTabs(activation.id, intl), location.pathname)
    : intl.formatMessage(sharedMessages.details);

  return (
    <React.Fragment>
      {routes()}
      <TopToolbar
        breadcrumbs={[
          {
            title: intl.formatMessage(sharedMessages.rulebookActivations),
            key: 'back-to-activations',
            to: '/activations',
          },
          {
            title: activation?.name,
            key: 'details',
            to: `/activation/${activation?.id}/details`,
          },
          {
            title: currentTab || intl.formatMessage(sharedMessages.details),
            key: 'current_tab',
          },
        ]}
      >
        <Level>
          <LevelItem>
            <Title headingLevel={'h2'}>{`${activation?.name}`}</Title>
          </LevelItem>
          <LevelItem>
            <Dropdown
              isPlain
              onSelect={() => setOpen(false)}
              position={DropdownPosition.right}
              toggle={<KebabToggle id="activation-details-toggle" onToggle={(isOpen) => setOpen(isOpen)} />}
              isOpen={isOpen}
              dropdownItems={dropdownItems}
            />
          </LevelItem>
        </Level>
      </TopToolbar>
      {activation && (
        <Switch>
          <Route exact path="/activation/:id/jobs">
            <ActivationJobs jobs={jobs} activation={activation} />
          </Route>
          <Route exact path="/activation/:id/stdout">
            <ActivationStdout activation={activation} />
          </Route>
          <Route path="/activation/:id">
            <ActivationDetails activation={activation} />
          </Route>
        </Switch>
      )}
    </React.Fragment>
  );
};

export { Activation };
