import { Title} from '@patternfly/react-core';
import { Route, Switch, useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';
import AppTabs from "@app/shared/app-tabs";

import {CaretLeftIcon} from "@patternfly/react-icons";
import {getServer} from "@app/utils/utils";
import {TopToolbar} from "@app/shared/top-toolbar";
import {ProjectDetails} from "@app/Project/project-details";
import {ProjectLinks} from "@app/Project/project-links";

export const renderProjectTabs = (projectId: string) => {
  const project_tabs = [
    {
      eventKey: 0,
      title: (
        <>
          <CaretLeftIcon />
          {'Back to Projects'}
        </>
      ),
      name: `/projects`,
    },
    { eventKey: 1, title: 'Details', name: `/project/${projectId}/details` },
    {
      eventKey: 2,
      title: 'Links',
      name: `/project/${projectId}/links`,
    }
  ];

  return <AppTabs tabItems={project_tabs}/>
};
const endpoint1 = 'http://' + getServer() + '/api/projects/';

const Project: React.FunctionComponent = () => {

  const [project, setProject] = useState([]);

  const { id } = useParams();
  console.log(id);


  useEffect(() => {
    fetch(endpoint1 + id, {
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
          title: 'Rulebook projects',
          to: '/projects'
        }
      ]
      }>
        <Title headingLevel={"h2"}>{`${project.name}`}</Title>
      </TopToolbar>
      <Switch>
        <Route exact path="/project/:id/links">
          <ProjectLinks
            project={project}
          />
        </Route>
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
