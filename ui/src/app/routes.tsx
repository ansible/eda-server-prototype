import * as React from 'react';
import { Route, RouteComponentProps, Switch } from 'react-router-dom';
import { Dashboard } from '@app/Dashboard/Dashboard';
import { Projects } from '@app/Projects/Projects';
import { Project } from '@app/Project/Project';
import { NewProject } from '@app/NewProject/NewProject';
import { EditProject } from '@app/EditProject/EditProject';
import { Activations } from '@app/Activations/Activations';
import { Activation } from '@app/Activation/Activation';
import { ActivationDetails } from '@app/Activation/activation-details';
import { ActivationJobs } from '@app/Activation/activation-jobs';
import { NewActivation } from '@app/NewActivation/NewActivation';
import { Jobs } from '@app/Jobs/Jobs';
import { Job } from '@app/Job/Job';
import { NewJob } from '@app/NewJob/NewJob';
import { RuleSets } from '@app/RuleSets/RuleSets';
import { RuleSet } from '@app/RuleSet/ruleset';
import { RuleBooks } from '@app/RuleBooks/RuleBooks';
import { RuleBook } from '@app/RuleBook/rulebook';
import { Inventories } from '@app/Inventories/Inventories';
import { Inventory } from '@app/Inventory/inventory';
import { Vars } from '@app/Vars/Vars';
import { Var } from '@app/Var/Var';
import { Playbooks } from '@app/Playbooks/Playbooks';
import { Playbook } from '@app/Playbook/Playbook';
import { NotFound } from '@app/NotFound/NotFound';
import { useDocumentTitle } from '@app/utils/useDocumentTitle';
import { ActivationStdout } from '@app/Activation/activation-stdout';
import { RulesetSources } from '@app/RuleSet/ruleset-sources';
import { RulesetDetails } from '@app/RuleSet/ruleset-details';
import { RulesetRules } from '@app/RuleSet/ruleset-rules';
import { Rules } from '@app/Rules/Rules';
import { Rule } from '@app/Rule/Rule';
import { Fragment } from 'react';
import { NewInventory } from '@app/NewInventory/NewInventory';
import { AuditView } from '@app/AuditView/AuditView';
import {AuditRules} from "@app/AuditView/audit-rules";
import {AuditHosts} from "@app/AuditView/audit-hosts";

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
    exact: true,
    label: 'Dashboard',
    path: '/dashboard',
    title: 'Main Dashboard',
  },
  {
    label: 'Management',
    routes: [
      {
        component: Projects,
        label: 'Projects',
        path: '/projects',
        title: 'Projects',
      },
      {
        component: Project,
        path: '/project/:id',
        title: 'Project',
      },
      {
        component: NewProject,
        path: '/new-project/',
        title: 'NewProject',
      },
      {
        component: EditProject,
        path: '/edit-project/:id',
        title: 'EditProject',
      },
      {
        component: Activations,
        label: 'Rulebook Activations',
        path: '/activations',
        title: 'Rulebook Activations',
      },
      {
        component: Activation,
        path: '/activation/:id',
        title: 'Activation',
      },
      {
        component: ActivationJobs,
        exact: true,
        path: '/activation/:id/jobs',
        title: 'Activation Jobs',
      },
      {
        component: ActivationDetails,
        exact: true,
        path: '/activation/:id/details',
        title: 'Activation Details',
      },
      {
        component: ActivationStdout,
        exact: true,
        path: '/activation/:id/stdout',
        title: 'Output',
      },
      {
        component: NewActivation,
        path: '/new-activation/',
        title: 'New Activation',
      },
      {
        component: Jobs,
        label: 'Jobs',
        path: '/jobs',
        title: 'Jobs',
      },
      {
        component: Job,
        path: '/job/:id',
        title: 'Job',
      },
      {
        component: NewJob,
        path: '/new-job/',
        title: 'NewJob',
      },
      {
        component: RuleBook,
        path: '/rulebooks/rulebook/:id',
        title: 'RuleBook',
      },
      {
        component: RuleBooks,
        label: 'Rulebooks',
        path: '/rulebooks',
        title: 'Rulebooks',
      },
      {
        component: RuleSets,
        label: 'Rule Sets',
        path: '/rulesets',
        title: 'Rule Sets',
      },
      {
        component: RuleSet,
        path: '/ruleset/:id',
        title: 'RuleSet',
      },
      {
        component: RulesetRules,
        exact: true,
        path: '/ruleset/:id/rules',
        title: 'Rules',
      },
      {
        component: RulesetDetails,
        exact: true,
        path: '/ruleset/:id/details',
        title: 'Details',
      },
      {
        component: RulesetSources,
        exact: true,
        path: '/ruleset/:id/sources',
        title: 'Sources',
      },
      {
        component: Rules,
        exact: true,
        label: 'Rules',
        path: '/rules',
        title: 'Rules',
      },
      {
        component: Rule,
        path: '/rule/:id',
        title: 'Rule',
      },
      {
        component: Inventory,
        path: '/inventories/inventory/:id',
        title: 'Inventory',
      },
      {
        component: Inventories,
        label: 'Inventories',
        path: '/inventories',
        title: 'Inventories',
      },
      {
        component: NewInventory,
        path: '/new-inventory/',
        title: 'New Inventory',
      },
      {
        component: Vars,
        exact: true,
        label: 'Extra Vars',
        path: '/vars',
        title: 'Extra Vars',
      },
      {
        component: Var,
        exact: true,
        path: '/var/:id',
        title: 'Var',
      },
      {
        component: Playbooks,
        exact: true,
        label: 'Playbooks',
        path: '/playbooks',
        title: 'Playbooks',
      },
      {
        component: Playbook,
        exact: true,
        path: '/playbook/:id',
        title: 'Playbook',
      },
    ],
  },
  {
    component: AuditView,
    label: 'Audit View',
    path: '/audit',
    title: 'Audit View',
  },
  {
    component: AuditRules,
    exact: true,
    path: '/audit/rules',
    title: 'Audit Rules',
  },
  {
    component: AuditHosts,
    exact: true,
    path: '/audit/hosts',
    title: 'Audit Hosts',
  },
];

const RouteWithTitleUpdates = ({ component: Component, title, ...rest }: IAppRoute) => {
  useDocumentTitle(title);

  function routeWithTitle(routeProps: RouteComponentProps) {
    return <Component {...rest} {...routeProps} />;
  }

  return <Route render={routeWithTitle} {...rest} />;
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
  return (
    <Fragment>
      <Switch>
        {flattenedRoutes.map(({ path, exact, component, title, isAsync }, idx) => (
          <RouteWithTitleUpdates
            path={path}
            exact={exact}
            component={component}
            key={idx}
            title={title}
            isAsync={isAsync}
          />
        ))}
        <PageNotFound title="404 Page Not Found" />
      </Switch>
    </Fragment>
  );
};

export { AppRoutes, routes };
