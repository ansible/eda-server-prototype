import * as React from 'react';
import { Route, RouteComponentProps, Switch } from 'react-router-dom';
import { Dashboard } from '@app/Dashboard/Dashboard';
import { Projects } from '@app/Projects/Projects';
import { Project } from '@app/Project/Project';
import { NewProject } from '@app/NewProject/NewProject';
import { Activations } from '@app/Activations/Activations';
import { Activation } from '@app/Activation/Activation';
import { ActivationDetails } from '@app/Activation/activation-details';
import { ActivationJobs } from '@app/Activation/activation-jobs';
import { NewActivation } from '@app/NewActivation/NewActivation';
import { Jobs } from '@app/Jobs/Jobs';
import { Job } from '@app/Job/Job';
import { NewJob } from '@app/NewJob/NewJob';
import { RuleSets } from '@app/RuleSetFiles/RuleSetFiles';
import { RuleSet } from '@app/RuleSetFile/ruleset';
import { Inventories } from '@app/Inventories/Inventories';
import { Inventory } from '@app/Inventory/Inventory';
import { Vars } from '@app/Vars/Vars';
import { Var } from '@app/Var/Var';
import { Playbooks } from '@app/Playbooks/Playbooks';
import { Playbook } from '@app/Playbook/Playbook';
import { NotFound } from '@app/NotFound/NotFound';
import { useDocumentTitle } from '@app/utils/useDocumentTitle';
import {ActivationStdout} from "@app/Activation/activation-stdout";
import {useIntl} from "react-intl";
import {RulesetSources} from "@app/RuleSetFile/ruleset-sources";
import {RulesetDetails} from "@app/RuleSetFile/ruleset-details";
import {RulesetRules} from "@app/RuleSetFile/ruleset-rules";

export interface IAppRoute {
  label?: string; // Excluding the label will exclude the route from the nav sidebar in AppLayout
  /* eslint-disable @typescript-eslint/no-explicit-any */
  component: React.ComponentType<RouteComponentProps<any>> | React.ComponentType<any>;
  /* eslint-enable @typescript-eslint/no-explicit-any */
  exact?: boolean;
  path: string;
  title: string;
  isAsync?: boolean;
  routes?: undefined;
}

export interface IAppRouteGroup {
  label: string;
  routes: IAppRoute[];
}

export type AppRouteConfig = IAppRoute | IAppRouteGroup;
const routes: AppRouteConfig[] = [
  {
    component: Dashboard,
    exact: false,
    label: 'Dashboard',
    path: '/eda/dashboard',
    title: 'Main Dashboard',
  },
  {
    component: Projects,
    exact: true,
    label: 'Projects',
    path: '/eda/projects',
    title: 'Projects',
  },
  {
    component: Project,
    path: '/eda/project/:id',
    title: 'Project',
  },
  {
    component: NewProject,
    path: '/eda/new-project/',
    title: 'NewProject',
  },
  {
    component: Activations,
    exact: true,
    label: 'Rulebook activations',
    path: '/eda/activations',
    title: 'Rulebook activations',
  },
  {
    component: Activation,
    path: '/eda/activation/:id',
    title: 'Activation',
  },
  {
    component: ActivationJobs,
    exact: true,
    path: '/eda/activation/:id/jobs',
    title: 'Activation jobs',
  },
  {
    component: ActivationDetails,
    exact: true,
    path: '/eda/activation/:id/details',
    title: 'Activation details',
  },
  {
    component: ActivationStdout,
    exact: true,
    path: '/eda/activation/:id/stdout',
    title: 'Standard out',
  },
  {
    component: NewActivation,
    path: '/eda/new-activation/',
    title: 'NewActivation',
  },
  {
    component: Jobs,
    exact: true,
    label: 'Jobs',
    path: '/eda/jobs',
    title: 'Jobs',
  },
  {
    component: Job,
    exact: true,
    path: '/eda/job/:id',
    title: 'Job',
  },
  {
    component: NewJob,
    path: '/eda/new-job/',
    title: 'NewJob',
  },
  {
    component: RuleSets,
    exact: true,
    label: 'Rule sets',
    path: '/eda/rulesets',
    title: 'Rule Sets',
  },
  {
    component: RuleSet,
    path: '/eda/ruleset/:id',
    title: 'RuleSet',
  },
  {
    component: RulesetRules,
    exact: true,
    path: '/eda/ruleset/:id/rules',
    title: 'Rules',
  },
  {
    component: RulesetDetails,
    exact: true,
    path: '/eda/ruleset/:id/details',
    title: 'Details',
  },
  {
    component: RulesetSources,
    exact: true,
    path: '/eda/ruleset/:id/sources',
    title: 'Sources',
  },

  {
    component: Inventories,
    exact: true,
    label: 'Inventories',
    path: '/eda/inventories',
    title: 'Inventories',
  },
  {
    component: Inventory,
    exact: true,
    path: '/eda/inventory/:id',
    title: 'Inventory',
  },
  {
    component: Vars,
    exact: true,
    label: 'Extra Vars',
    path: '/eda/vars',
    title: 'Extra Vars',
  },
  {
    component: Var,
    exact: true,
    path: '/eda/var/:id',
    title: 'Var',
  },
  {
    component: Playbooks,
    exact: true,
    label: 'Playbooks',
    path: '/eda/playbooks',
    title: 'Playbooks',
  },
  {
    component: Playbook,
    exact: true,
    path: '/eda/playbook/:id',
    title: 'Playbook',
  }
];

const RouteWithTitleUpdates = ({ component: Component, title, ...rest }: IAppRoute) => {
  useDocumentTitle(title);

  function routeWithTitle(routeProps: RouteComponentProps) {
    return <Component {...rest} {...routeProps} />;
  }

  return <Route render={routeWithTitle} {...rest}/>;
};

const PageNotFound = ({ title }: { title: string }) => {
  useDocumentTitle(title);
  return <Route component={NotFound} />;
};

const flattenedRoutes: IAppRoute[] = routes.reduce(
  (flattened, route) => [...flattened, ...(route.routes ? route.routes : [route])],
  [] as IAppRoute[]
);

const AppRoutes = (): React.ReactElement => {
  return (<Switch>
    {flattenedRoutes.map(({path, exact, component, title, isAsync}, idx) => (
      <RouteWithTitleUpdates
        path={path}
        exact={exact}
        component={component}
        key={idx}
        title={title}
        isAsync={isAsync}
      />
    ))}
    <Route component={Dashboard} />
  </Switch>);
}

export { AppRoutes, routes };
