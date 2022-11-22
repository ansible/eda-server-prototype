// eslint-disable-next-line @typescript-eslint/no-var-requires
const { defineMessages } = require('react-intl');

const sharedMessages = defineMessages({
  name: {
    id: 'shared.name',
    defaultMessage: 'Name',
  },
  url: {
    id: 'shared.url',
    defaultMessage: 'Url',
  },
  add: {
    id: 'shared.add',
    defaultMessage: 'Add',
  },
  edit: {
    id: 'shared.edit',
    defaultMessage: 'Edit',
  },
  delete: {
    id: 'shared.delete',
    defaultMessage: 'Delete',
  },
  disable: {
    id: 'shared.disable',
    defaultMessage: 'Disable',
  },
  search: {
    id: 'shared.search',
    defaultMessage: 'Search',
  },
  lastModified: {
    id: 'shared.lastModified',
    defaultMessage: 'Last modified',
  },
  description: {
    id: 'shared.description',
    defaultMessage: 'Description',
  },
  details: {
    id: 'shared.details',
    defaultMessage: 'Details',
  },
  created: {
    id: 'shared.created',
    defaultMessage: 'Created',
  },
  type: {
    id: 'shared.type',
    defaultMessage: 'Type',
  },
  revision: {
    id: 'shared.revision',
    defaultMessage: 'Revision',
  },
  filterByName: {
    id: 'shared.filterByName',
    defaultMessage: 'Filter by {name}',
  },
  noResultsFound: {
    id: 'shared.noResultsFound',
    defaultMessage: 'No results found',
  },
  noResult: {
    id: 'shared.noResult',
    defaultMessage: 'No {results}',
  },
  job: {
    id: 'shared.job',
    defaultMessage: 'Job',
  },
  jobs: {
    id: 'shared.jobs',
    defaultMessage: 'Jobs',
  },
  sync: {
    id: 'shared.sync',
    defaultMessage: 'Sync',
  },
  launch: {
    id: 'shared.launch',
    defaultMessage: 'Launch',
  },
  relaunch: {
    id: 'shared.relaunch',
    defaultMessage: 'Relaunch',
  },
  restart: {
    id: 'shared.restart',
    defaultMessage: 'Restart',
  },
  selected: {
    id: 'shared.selected',
    defaultMessage: 'Selected',
  },
  addJob: {
    id: 'activation.addJob',
    defaultMessage: 'Add job',
  },
  deleteJobTitle: {
    id: 'activation.deleteJob',
    defaultMessage: 'Delete job',
  },
  status: {
    id: 'shared.status',
    defaultMessage: 'Status',
  },
  cancel: {
    id: 'shared.cancel',
    defaultMessage: 'Cancel',
  },
  rule: {
    id: 'shared.rule',
    defaultMessage: 'Rule',
  },
  clearAllFilters: {
    id: 'shared.clearAllFilters',
    defaultMessage: 'Clear all filters',
  },
  clearAllFiltersDescription: {
    id: 'shared.clearAllFiltersDescription',
    defaultMessage: 'No results match the filter criteria. Remove all filters or clear all filters to show results.',
  },
  ariaLabel: {
    id: 'shared.ariaLabel',
    defaultMessage: '{name} table',
  },
  updatedLabel: {
    id: 'shared.updatedLabel',
    defaultMessage: 'Updated',
  },
  allFieldsRequired: {
    id: 'shared.allFieldsRequired',
    defaultMessage: 'All fields are required',
  },
  output: {
    id: 'shared.output',
    defaultMessage: 'Output',
  },
  rulebookActivations: {
    id: 'shared.rulebookActivations',
    defaultMessage: 'Rulebook Activations',
  },
  namePlaceholder: {
    id: 'shared.namePlaceholder',
    defaultMessage: 'Insert name here',
  },
  descriptionPlaceholder: {
    id: 'shared.descriptionPlaceholder',
    defaultMessage: 'Insert description here',
  },
  rules: {
    id: 'shared.rules',
    defaultMessage: 'Rules',
  },
  sources: {
    id: 'shared.sources',
    defaultMessage: 'Sources',
  },
  error: {
    id: 'shared.error',
    defaultMessage: 'Error',
  },
  host: {
    id: 'shared.host',
    defaultMessage: 'Hosts',
  },
  hosts: {
    id: 'shared.hosts',
    defaultMessage: 'Hosts',
  },
  project: {
    id: 'project.project',
    defaultMessage: 'Project',
  },
  projects: {
    id: 'project.projects',
    defaultMessage: 'Projects',
  },
  noprojects_action: {
    id: 'project.noprojects_action',
    defaultMessage: 'Please add a project by using the button below.',
  },
  noprojects_description: {
    id: 'project.noprojects_description',
    defaultMessage: 'There are currently no projects added for your organization.',
  },
  add_new_project: {
    id: 'project.addNewProject',
    defaultMessage: 'Add new project',
  },
  projectRemoveTitle: {
    id: 'project.removeProject',
    defaultMessage: 'Delete project',
  },
  projectsRemoveTitle: {
    id: 'project.removeProjects',
    defaultMessage: 'Delete selected projects',
  },
  projectRemoveDescription: {
    id: 'project.removeProjectDescription',
    defaultMessage: 'Are you sure you want to delete the project below?',
  },
  projectsRemoveDescription: {
    id: 'project.removeProjectDescription',
    defaultMessage: 'Are you sure you want to delete the selected projects?',
  },
  projectPlaceholder: {
    id: 'activation.projectPlaceholder',
    defaultMessage: 'Select project',
  },
  addProject: {
    id: 'project.addProject',
    defaultMessage: 'Add project',
  },
  editProject: {
    id: 'project.editProject',
    defaultMessage: 'Update project',
  },
  deleteProjectTitle: {
    id: 'project.deleteProject',
    defaultMessage: 'Delete project',
  },
  backToProjects: {
    id: 'project.backToProjects',
    defaultMessage: 'Back to Projects',
  },
  project_link: {
    id: 'project.project_link',
    defaultMessage: 'Project link',
  },
  scmUrl: {
    id: 'project.scmUrl',
    defaultMessage: 'SCM URL',
  },
  scmType: {
    id: 'project.scmType',
    defaultMessage: 'SCM type',
  },
  scmCredentials: {
    id: 'project.scmCredentials',
    defaultMessage: 'SCM Credentials',
  },
  scmToken: {
    id: 'project.scmToken',
    defaultMessage: 'SCM token',
  },
  scmUrlPlaceholder: {
    id: 'project.scmUrlPlaceholder',
    defaultMessage: 'Insert SCM URL here',
  },
  scmTypePlaceholder: {
    id: 'project.scmTypePlaceholder',
    defaultMessage: 'SCM Type',
  },
  scmCredentialsPlaceholder: {
    id: 'project.scmCredentialsPlaceholder',
    defaultMessage: 'Select an SCM Credential',
  },
  scmTokenPlaceholder: {
    id: 'project.scmTokenPlaceholder',
    defaultMessage: 'Select an SCM Token',
  },
  add_project_success: {
    id: 'project.addProjectSuccess',
    defaultMessage: 'Project added successfully',
  },
  add_project_failure: {
    id: 'project.addProjectFailure',
    defaultMessage: 'Error adding new project',
  },
  edit_project_success: {
    id: 'project.editProjectSuccess',
    defaultMessage: 'Project updated successfully',
  },
  edit_project_failure: {
    id: 'project.editProjectFailure',
    defaultMessage: 'Error updating project',
  },
  delete_project_success: {
    id: 'project.deleteProjectSuccess',
    defaultMessage: 'Project removed successfully',
  },
  delete_project_failure: {
    id: 'project.deleteProjectFailure',
    defaultMessage: 'Remove project failed',
  },
  enterProjectName: {
    id: 'project.enterProjectName',
    defaultMessage: 'Enter project name',
  },
  enterScmUrl: {
    id: 'project.enterScm',
    defaultMessage: 'Enter SCM URL',
  },
  activation: {
    id: 'activation.activation',
    defaultMessage: 'Activation',
  },
  activationRemoveTitle: {
    id: 'activation.removeActivation',
    defaultMessage: 'Delete rulebook activation',
  },
  activationsRemoveTitle: {
    id: 'activation.removeActivations',
    defaultMessage: 'Delete selected rulebook activations',
  },
  activationRemoveDescription: {
    id: 'activation.removeActivationDescription',
    defaultMessage: 'Are you sure you want to delete the rulebook activation below?',
  },
  activationsRemoveDescription: {
    id: 'activation.removeActivationsDescription',
    defaultMessage: 'Are you sure you want to delete the selected rulebook activations?',
  },
  activations: {
    id: 'activation.activations',
    defaultMessage: 'Rulebook Activations',
  },
  noactivations_description: {
    id: 'activation.noactivations_description',
    defaultMessage: 'There are currently no rulebook activations added for your organization.',
  },
  noactivations_action: {
    id: 'activation.noactivations_action',
    defaultMessage: 'Please add a rulebook activation by using the button below.',
  },
  addActivation: {
    id: 'activation.addActivation',
    defaultMessage: 'Add rulebook activation',
  },
  deleteActivationTitle: {
    id: 'activation.deleteActivation',
    defaultMessage: 'Delete activation',
  },
  activation_status: {
    id: 'activations.activation_status',
    defaultMessage: 'Activation status',
  },
  enterRulebookActivationName: {
    id: 'activation.enterRulebookActivationName',
    defaultMessage: 'Enter a rulebook activation name',
  },
  enterRulebookActivationDescription: {
    id: 'activation.enterRulebookActivationDescription',
    defaultMessage: 'Enter a rulebook activation description',
  },
  selectRuleSet: {
    id: 'activation.selectRulebookActivationName',
    defaultMessage: 'Select a rule set',
  },
  selectRestartPolicy: {
    id: 'activation.selectRestartPolicy',
    defaultMessage: 'Select a restart policy',
  },
  selectPlaybook: {
    id: 'job.selectPlaybookName',
    defaultMessage: 'Select a playbook',
  },
  selectInventory: {
    id: 'activation.selectInventory',
    defaultMessage: 'Select an inventory',
  },
  selectExtraVar: {
    id: 'activation.selectExtraVar',
    defaultMessage: 'Select extra variables',
  },
  selectProject: {
    id: 'activation.selectProject',
    defaultMessage: 'Select project',
  },
  add_activation_success: {
    id: 'activation.addActivationSuccess',
    defaultMessage: 'Rulebook activation added successfully',
  },
  add_activation_failure: {
    id: 'activation.addActivationFailure',
    defaultMessage: 'Error adding new rulebook activation',
  },
  edit_activation_success: {
    id: 'activation.editActivationSuccess',
    defaultMessage: 'Rulebook activation updated successfully',
  },
  edit_activation_failure: {
    id: 'activation.editActivationFailure',
    defaultMessage: 'Error updating the rulebook activation',
  },
  delete_activation_success: {
    id: 'activation.deleteActivationSuccess',
    defaultMessage: 'Rulebook activation removed successfully',
  },
  delete_activation_failure: {
    id: 'activation.deleteActivationFailure',
    defaultMessage: 'Remove rulebook activation failed',
  },
  ruleset: {
    id: 'rulesets.ruleset',
    defaultMessage: 'Rule set',
  },
  rulesets: {
    id: 'rulesets.rulesets',
    defaultMessage: 'Rule sets',
  },
  norulesets: {
    id: 'rulesets.norulesets',
    defaultMessage: 'No rule sets',
  },
  number_of_rules: {
    id: 'rulesets.number_of_rules',
    defaultMessage: 'Number of rules',
  },
  fire_count: {
    id: 'rulesets.fire_count',
    defaultMessage: 'Fire count',
  },
  deleteRuleSetTitle: {
    id: 'rulesets.deleteRuleSet',
    defaultMessage: 'Delete rule set',
  },
  backToRuleSets: {
    id: 'ruleset.backToRuleSets',
    defaultMessage: 'Back to Rule Sets',
  },
  norulesetrules: {
    id: 'ruleset.norulesetrules',
    defaultMessage: 'No rules for this rule set',
  },
  norulesetsources: {
    id: 'ruleset.norulesetsources',
    defaultMessage: 'No sources for this rule set',
  },
  noactivationjobs: {
    id: 'activation.nojobs_description',
    defaultMessage: 'There are currently no jobs for this rulebook activation.',
  },
  nojobs_description: {
    id: 'common.nojobs_description',
    defaultMessage: 'There are currently no jobs for your organization.',
  },
  nojobs_action: {
    id: 'common.nojobs_action',
    defaultMessage: 'Please add a job by using the button below.',
  },
  lastFiredDate: {
    id: 'activation.lastFiredDate',
    defaultMessage: 'Last fired date',
  },
  edaContainerImage: {
    id: 'activation.edaContainerImage',
    defaultMessage: 'EDA container image',
  },
  edaContainerImagePlaceholder: {
    id: 'activation.edaContainerImagePlaceholder',
    defaultMessage: 'Insert an EDA container image here',
  },
  restartPolicyPlaceholder: {
    id: 'activation.restartPolicyPlaceholder',
    defaultMessage: 'Select a restart policy',
  },
  inventoryPlaceholder: {
    id: 'activation.inventoryPlaceholder',
    defaultMessage: 'Select an inventory',
  },
  playbookPlaceholder: {
    id: 'activation.playbookPlaceholder',
    defaultMessage: 'Select a playbook',
  },
  ruleSetPlaceholder: {
    id: 'activation.ruleSetPlaceholder',
    defaultMessage: 'Select a rule set',
  },
  backToRulebookActivations: {
    id: 'activation.backToRulebookActivations',
    defaultMessage: 'Back to Rulebook Activations',
  },
  extraVarPlaceholder: {
    id: 'project.extraVarPlaceholder',
    defaultMessage: 'Select extra variables',
  },
  action: {
    id: 'rule.action',
    defaultMessage: 'Action',
  },
  condition: {
    id: 'rule.condition',
    defaultMessage: 'Condition',
  },
  backToRules: {
    id: 'rule.backToRules',
    defaultMessage: 'Back to Rules',
  },
  workingDirectory: {
    id: 'shared.workingDirectory',
    defaultMessage: 'Working directory',
  },
  workingDirectoryPlaceholder: {
    id: 'shared.workingDirectoryPlaceholder',
    defaultMessage: 'Working directory',
  },
  enterRulebookActivationWorkingDirectory: {
    id: 'activation.enterRulebookActivationWorkingDirectory',
    defaultMessage: 'Enter a rulebook working directory',
  },
  backToRuleBooks: {
    id: 'rulebook.backToRuleBooks',
    defaultMessage: 'Back to Rulebooks',
  },
  rulebooks: {
    id: 'rulebook.rulebooks',
    defaultMessage: 'Rulebooks',
  },
  rulebook: {
    id: 'rulebook.rulebook',
    defaultMessage: 'Rulebook',
  },
  norulebooks: {
    id: 'rulebook.norulebooks',
    defaultMessage: 'There are currently no rulebooks for your organization',
  },
  norulebookrulesets: {
    id: 'rulebook.norulebookrulesets',
    defaultMessage: 'No rule sets for this rulebook',
  },
  number_of_rulesets: {
    id: 'rulebook.number_of_ruesets',
    defaultMessage: 'Number of rulesets',
  },
  jobRemoveTitle: {
    id: 'job.removeJob',
    defaultMessage: 'Delete job',
  },
  jobsRemoveTitle: {
    id: 'job.removeJobs',
    defaultMessage: 'Delete jobs',
  },
  jobRemoveDescription: {
    id: 'job.removeJobDescription',
    defaultMessage: 'Are you sure you want to delete the job below?',
  },
  jobsRemoveDescription: {
    id: 'job.removeJobsDescription',
    defaultMessage: 'Are you sure you want to delete the selected jobs?',
  },
  add_job_success: {
    id: 'job.addProjectSuccess',
    defaultMessage: 'Job added successfully',
  },
  add_job_failure: {
    id: 'job.addJobFailure',
    defaultMessage: 'Error adding new job',
  },
  delete_job_success: {
    id: 'job.deleteJobSuccess',
    defaultMessage: 'Job removed successfully',
  },
  delete_job_failure: {
    id: 'job.deleteJobFailure',
    defaultMessage: 'Remove job failed',
  },
  inventory: {
    id: 'inventory.inventory',
    defaultMessage: 'Inventory',
  },
  inventories: {
    id: 'inventory.inventories',
    defaultMessage: 'Inventories',
  },
  noinventories_action: {
    id: 'inventory.noinventories_action',
    defaultMessage: 'Please add an inventory by using the button below.',
  },
  noinventories_description: {
    id: 'inventory.noinventories_description',
    defaultMessage: 'There are currently no inventories added for your organization.',
  },
  add_new_inventory: {
    id: 'inventory.addNewInventory',
    defaultMessage: 'Add new inventory',
  },
  inventoryRemoveTitle: {
    id: 'inventory.removeInventory',
    defaultMessage: 'Delete inventory',
  },
  inventoriesRemoveTitle: {
    id: 'inventory.removeInventories',
    defaultMessage: 'Delete inventories',
  },
  inventoryRemoveDescription: {
    id: 'inventory.removeInventoryDescription',
    defaultMessage: 'Are you sure you want to delete the inventory below?',
  },
  inventoriesRemoveDescription: {
    id: 'inventory.removeInventoriesDescription',
    defaultMessage: 'Are you sure you want to delete the selected inventories?',
  },
  addInventory: {
    id: 'inventory.addInventory',
    defaultMessage: 'Add inventory',
  },
  deleteInventoryTitle: {
    id: 'inventory.deleteInventory',
    defaultMessage: 'Delete inventory',
  },
  backToInventories: {
    id: 'project.backToInventories',
    defaultMessage: 'Back to Inventories',
  },
  source_of_inventory: {
    id: 'inventory.source_of_inventory',
    defaultMessage: 'Source of inventory',
  },
  enterInventoryName: {
    id: 'inventory.enterInventoryName',
    defaultMessage: 'Enter an inventory name',
  },
  enterInventoryDescription: {
    id: 'inventory.enterInventoryDescription',
    defaultMessage: 'Enter an inventory description',
  },
  add_inventory_success: {
    id: 'inventory.addInventorySuccess',
    defaultMessage: 'Inventory added successfully',
  },
  add_inventory_failure: {
    id: 'inventory.addInventoryFailure',
    defaultMessage: 'Error adding new inventory',
  },
  delete_inventory_success: {
    id: 'inventory.deleteInventorySuccess',
    defaultMessage: 'Inventory removed successfully',
  },
  delete_inventory_failure: {
    id: 'inventory.deleteInventoryFailure',
    defaultMessage: 'Remove inventory failed',
  },
  audit_view_title: {
    id: 'audit.auditViewTitle',
    defaultMessage: 'Audit View',
  },
  audit_rules_title: {
    id: 'audit.auditRulesTitle',
    defaultMessage: 'Rules recently fired',
  },
  audit_hosts_title: {
    id: 'audit.auditHostsTitle',
    defaultMessage: 'Hosts recently changed',
  },
  norulesrecentlyfired: {
    id: 'audit.norulesrecentlyfired',
    defaultMessage: 'No rules recently fired',
  },
  nohostsrecentlychanged: {
    id: 'host.nohostsrecentlychnaged',
    defaultMessage: 'No hosts recently changed',
  },
  backToAuditView: {
    id: 'audit.backToAuditView',
    defaultMessage: 'Back to Audit View',
  },
  noauditrulejobs: {
    id: 'common.noauditrulejobs',
    defaultMessage: 'There are currently no jobs for this rule.',
  },
  noauditrulehosts: {
    id: 'common.noauditrulehosts',
    defaultMessage: 'There are currently no hosts for this rule.',
  },
  noauditruleevents: {
    id: 'common.noauditruleevents',
    defaultMessage: 'There are currently no events for this rule.',
  },
  increment_counter: {
    id: 'common.increment_counter',
    defaultMessage: 'Increment counter',
  },
  source_type: {
    id: 'common.source_type',
    defaultMessage: 'Source type',
  },
  timestamp: {
    id: 'common.timestamp',
    defaultMessage: 'Timestamp',
  },
  event: {
    id: 'common.event',
    defaultMessage: 'Event',
  },
  events: {
    id: 'common.events',
    defaultMessage: 'Events',
  },
});

export default sharedMessages;
