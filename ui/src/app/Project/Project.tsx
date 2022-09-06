import { Title} from '@patternfly/react-core';
import { Route, Switch, useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import AppTabs from "@app/shared/app-tabs";

import {CaretLeftIcon} from "@patternfly/react-icons";
import {getServer} from "@app/utils/utils";
import {TopToolbar} from "@app/shared/top-toolbar";
import {ProjectDetails} from "@app/Project/project-details";
import {ProjectLinks} from "@app/Project/project-links";
import sharedMessages from "../messages/shared.messages";
import {useIntl} from "react-intl";
import {ProjectType} from "@app/shared/types/common-types";

export const renderProjectTabs = (intl, projectId: string | undefined) => {
  const project_tabs = [
    {
      eventKey: 0,
      title: (
        <div>
          <CaretLeftIcon />
          {intl.formatMessage(sharedMessages.backToProjects)}
        </div>
      ),
      name: `/projects`,
    },
    { eventKey: 1, title: intl.formatMessage(sharedMessages.details), name: `/project/${projectId}/details` },
    {
      eventKey: 2,
      title: 'Links',
      name: `/project/${projectId}/links`,
    }
  ];

  return <AppTabs tabItems={project_tabs}/>
};
const endpoint_project = 'http://' + getServer() + '/api/projects/';

const Project: React.FunctionComponent = () => {

  const [project, setProject] = useState<ProjectType>();
  const { id } = useParams<{id:string}>();
  const intl = useIntl();

  useEffect(() => {
    fetch(endpoint_project + id, {
      headers: {
        'Content-Type': 'application/json',
      },
    }).then(response => response.json())
      .then(data => setProject(data));
  }, []);

  return (
    <React.Fragment>
      <TopToolbar breadcrumbs={[
        {
          title: intl.formatMessage(sharedMessages.projects),
          to: '/projects'
        },
        {
          title:`${project?.name}`
        },
      ]
      }>
        <Title headingLevel={"h2"}>{`${project?.name}`}</Title>
      </TopToolbar>
      <Switch>
        { project && <Route exact path="/project/:id/links">
          <ProjectLinks
            project={project}
          />
        </Route> }
        <Route path="/project/:id">
          <ProjectDetails
            project={project}
          />
        </Route>
      </Switch>
    </React.Fragment>
  );
}

export { Project };
