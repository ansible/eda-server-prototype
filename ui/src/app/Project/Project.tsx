import {
  Dropdown, DropdownItem,
  DropdownPosition,
  KebabToggle, Level, LevelItem,
  Title
} from '@patternfly/react-core';
import {Link, Route, Switch, useLocation, useParams} from 'react-router-dom';
import React, {useState, useEffect, Fragment} from 'react';
import AppTabs from "@app/shared/app-tabs";

import {CaretLeftIcon} from "@patternfly/react-icons";
import {getServer, getTabFromPath} from "@app/utils/utils";
import {TopToolbar} from "@app/shared/top-toolbar";
import {ProjectDetails} from "@app/Project/project-details";
import {ProjectLinks} from "@app/Project/project-links";
import sharedMessages from "../messages/shared.messages";
import {useIntl} from "react-intl";
import {AnyObject, ProjectType, TabItemType} from "@app/shared/types/common-types";
import {NewProject} from "@app/NewProject/NewProject";
import {EditProject} from "@app/EditProject/EditProject";
import {RemoveProject} from "@app/RemoveProject/RemoveProject";

const buildProjectTabs = (projectId: string, intl: AnyObject) : TabItemType[] => ( [
  {
    eventKey: 0,
    title: (
      <div>
        <CaretLeftIcon/>
        {intl.formatMessage(sharedMessages.backToProjects)}
      </div>
    ),
    name: `/projects`
  },
  { eventKey: 1,
    title: 'Details',
    name: `/projects/project/${projectId}/details`
  },
  {
    eventKey: 2,
    title: 'Links',
    name: `/project/${projectId}/links`,
  }
]);

export const renderProjectTabs = (projectId: string, intl) => {
  const project_tabs = buildProjectTabs(projectId, intl);
  return <AppTabs tabItems={project_tabs}/>
};

const endpoint_project = 'http://' + getServer() + '/api/projects';

const Project: React.FunctionComponent = () => {

  const [project, setProject] = useState<ProjectType>();
  const [isOpen, setOpen] = useState<boolean>(false);
  const { id } = useParams<{id:string}>();
  const intl = useIntl();

  const dropdownItems = [
    <DropdownItem
      aria-label="Edit"
      key="edit-project"
      id="edit-project"
      component={ <Link to={`/edit-project/${id}`}>
          {intl.formatMessage(sharedMessages.edit)}
        </Link>
      }
      role="link"
    />,
    <DropdownItem
      aria-label="Sync"
      key="sync-project"
      id="sync-project"
      component={ <Link to={`/project/${id}/sync`}>
        {intl.formatMessage(sharedMessages.sync)}
      </Link>
      }
      role="link"
    />,
    <DropdownItem
      aria-label="Delete"
      key="delete-project"
      id="delete-project"
      component={ <Link to={`/project/${id}/remove`}>
        {intl.formatMessage(sharedMessages.delete)}
      </Link>
      }
      role="link"
    />
  ]

  const routes = () => <Fragment>
    <Route exact path="/project/:id/remove"
           render={ (props: AnyObject) => <RemoveProject {...props}/> }/>
  </Fragment>;

  useEffect(() => {
    fetch(`${endpoint_project}/${id}`, {
      headers: {
        'Content-Type': 'application/json',
      },
    }).then(response => response.json())
      .then(data => setProject(data));
  }, []);
  const location = useLocation();
  const currentTab = project?.id ?
    getTabFromPath(buildProjectTabs(project.id,intl), location.pathname) :
    intl.formatMessage(sharedMessages.details);
  return (
    <React.Fragment>
      { routes() }
      <TopToolbar breadcrumbs={[
        {
          title: intl.formatMessage(sharedMessages.projects),
          to: '/projects'
        },
        {
          title: project?.name,
          key: 'details',
          to: `/project/${project?.id}/details`
        },
        {
          title: currentTab || intl.formatMessage(sharedMessages.details),
          key: 'current_tab'
        }
      ]
      }>
        <Level>
          <LevelItem>
            <Title headingLevel={"h2"}>{`${project?.name}`}</Title>
          </LevelItem>
          <LevelItem>
            <Dropdown
              isPlain
              onSelect={() => setOpen(false)}
              position={DropdownPosition.right}
              toggle={
              <KebabToggle
                id="project-details-toggle"
                onToggle={(isOpen) => setOpen(isOpen)}
              />}
              isOpen={isOpen}
              dropdownItems={dropdownItems}
              />
          </LevelItem>
        </Level>
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
