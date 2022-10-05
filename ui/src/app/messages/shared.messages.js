// eslint-disable-next-line @typescript-eslint/no-var-requires
const { defineMessages } = require('react-intl');

const sharedMessages = defineMessages({
  name: {
    id: 'shared.name',
    defaultMessage: 'Name'
  },
  url: {
    id: 'shared.url',
    defaultMessage: 'Url'
  },
  add: {
    id: 'shared.add',
    defaultMessage: 'Add'
  },
  edit: {
    id: 'shared.edit',
    defaultMessage: 'Edit'
  },
  delete: {
    id: 'shared.delete',
    defaultMessage: 'Delete'
  },
  disable: {
    id: 'shared.disable',
    defaultMessage: 'Disable'
  },
  search: {
    id: 'shared.search',
    defaultMessage: 'Search'
  },
  lastModified: {
    id: 'shared.lastModified',
    defaultMessage: 'Last modified'
  },
  description: {
    id: 'shared.description',
    defaultMessage: 'Description'
  },
  details: {
    id: 'shared.details',
    defaultMessage: 'Details'
  },
  created: {
    id: 'shared.created',
    defaultMessage: 'Created'
  },
  type: {
    id: 'shared.type',
    defaultMessage: 'Type'
  },
  revision: {
    id: 'shared.revision',
    defaultMessage: 'Revision'
  },
  filterByName: {
    id: 'shared.filterByName',
    defaultMessage: 'Filter by {name}'
  },
  noResultsFound: {
    id: 'shared.noResultsFound',
    defaultMessage: 'No results found'
  },
  noResult: {
    id: 'shared.noResult',
    defaultMessage: 'No {results}'
  },
  job: {
    id: 'shared.job',
    defaultMessage: 'Job'
  },
  jobs: {
    id: 'shared.jobs',
    defaultMessage: 'Jobs'
  },
  addJob: {
    id: 'activation.addJob',
    defaultMessage: 'Add job'
  },
  deleteJobTitle: {
    id: 'activation.deleteJob',
    defaultMessage: 'Delete job'
  },
  status: {
    id: 'shared.status',
    defaultMessage: 'Status'
  },
  cancel: {
    id: 'shared.cancel',
    defaultMessage: 'Cancel'
  },
  rule: {
    id: 'shared.rule',
    defaultMessage: 'Rule'
  },
  clearAllFilters: {
    id: 'shared.clearAllFilters',
    defaultMessage: 'Clear all filters'
  },
  clearAllFiltersDescription: {
    id: 'shared.clearAllFiltersDescription',
    defaultMessage:
      'No results match the filter criteria. Remove all filters or clear all filters to show results.'
  },
  ariaLabel: {
    id: 'shared.ariaLabel',
    defaultMessage: '{name} table'
  },
  updatedLabel: {
    id: 'shared.updatedLabel',
    defaultMessage: 'Updated'
  },
  allFieldsRequired: {
    id: 'shared.allFieldsRequired',
    defaultMessage: 'All fields are required'
  },
  output: {
    id: 'shared.output',
    defaultMessage: 'Output'
  },
  rulebookActivations: {
    id: 'shared.rulebookActivations',
    defaultMessage: 'Rulebook Activations'
  },
  namePlaceholder: {
    id: 'shared.namePlaceholder',
    defaultMessage: 'Insert name here'
  },
  descriptionPlaceholder: {
    id: 'shared.descriptionPlaceholder',
    defaultMessage: 'Insert description here'
  },
  rules: {
    id: 'shared.rules',
    defaultMessage: 'Rules'
  },
  sources: {
    id: 'shared.sources',
    defaultMessage: 'Sources'
  },
  project: {
    id: 'project.project',
    defaultMessage: 'Project'
  },
  projects: {
    id: 'project.projects',
    defaultMessage: 'Projects'
  },
  noprojects_action: {
    id: 'project.noprojects_action',
    defaultMessage: 'Please add a project by using the button below.'
  },
  noprojects_description: {
    id: 'project.noprojects_description',
    defaultMessage: 'There are currently no projects added for your organization.'
  },
  add_new_project: {
    id: 'project.addNewProject',
    defaultMessage: 'Add new project'
  },
  projectRemoveTitle: {
    id: 'project.removeProject',
    defaultMessage: 'Delete project'
  },
  projectRemoveDescription: {
    id: 'project.removeProjectDescription',
    defaultMessage: 'Are you sure you want to delete the project below?'
  },
  addProject: {
    id: 'project.addProject',
    defaultMessage: 'Add project'
  },
  deleteProjectTitle: {
    id: 'project.deleteProject',
    defaultMessage: 'Delete project'
  },
  backToProjects: {
    id: 'project.backToProjects',
    defaultMessage: 'Back to Projects'
  },
  project_link: {
  id: 'project.project_link',
    defaultMessage: 'Project link'
},
  scmUrl: {
    id: 'project.scmUrl',
    defaultMessage: 'SCM URL'
  },
  scmType: {
    id: 'project.scmType',
    defaultMessage: 'SCM Type'
  },
  scmCredentials: {
    id: 'project.scmCredentials',
    defaultMessage: 'SCM Credentials'
  },
  scmToken: {
    id: 'project.scmToken',
    defaultMessage: 'SCM Token'
  },
  scmUrlPlaceholder: {
    id: 'project.scmUrlPlaceholder',
    defaultMessage: 'Insert SCM URL here'
  },
  scmTypePlaceholder: {
    id: 'project.scmTypePlaceholder',
    defaultMessage: 'SCM Type'
  },
  scmCredentialsPlaceholder: {
    id: 'project.scmCredentialsPlaceholder',
    defaultMessage: 'Select an SCM Credential'
  },
  scmTokenPlaceholder: {
    id: 'project.scmTokenPlaceholder',
    defaultMessage: 'Select an SCM Token'
  },
  activation: {
    id: 'activation.activation',
    defaultMessage: 'Activation'
  },
  activationRemoveTitle: {
    id: 'activation.removeActivation',
    defaultMessage: 'Delete rulebook activation'
  },
  activationRemoveDescription: {
    id: 'activation.removeActivationDescription',
    defaultMessage: 'Are you sure you want to delete the rulebook activation below?'
  },
  activations: {
    id: 'activation.activations',
    defaultMessage: 'Rulebook activations'
  },
  noactivations_description: {
    id: 'activation.noactivations_description',
    defaultMessage: 'There are currently no rulebook activations added for your organization.'
  },
  noactivations_action: {
    id: 'activation.noactivations_action',
    defaultMessage: 'Please add a rulebook activation by using the button below.'
  },
  addActivation: {
    id: 'activation.addActivation',
    defaultMessage: 'Add rulebook activation'
  },
  deleteActivationTitle: {
    id: 'activation.deleteActivation',
    defaultMessage: 'Delete activation'
  },
  activation_status: {
    id: 'activations.activation_status',
    defaultMessage: 'Activation status'
  },
  enterRulebookActivationName: {
    id: 'activation.enterRulebookActivationName',
    defaultMessage: 'Insert name here'
  },
  enterRulebookActivationDescription: {
    id: 'activation.enterRulebookActivationDescription',
    defaultMessage: 'Insert description here'
  },
  selectRuleBook: {
    id: 'activation.selectRulebookActivationName',
    defaultMessage: 'Select a Rulebook'
  },
  selectExecutionEnvironment: {
    id: 'activation.selectExecutionEnvironment',
    defaultMessage: 'Select a execution environment'
  },
  selectRestartPolicy: {
    id: 'activation.selectRestartPolicy',
    defaultMessage: 'Select a restart policy'
  },
  selectPlaybook: {
    id: 'job.selectPlaybookName',
    defaultMessage: 'Select a playbook'
  },
  selectInventory: {
    id: 'activation.selectInventory',
    defaultMessage: 'Select an inventory'
  },
  selectExtraVar: {
    id: 'activation.selectExtraVar',
    defaultMessage: 'Select extra variables'
  },
  ruleset: {
    id: 'rulesets.ruleset',
    defaultMessage: 'Rule set'
  },
  rulesets: {
    id: 'rulesets.rulesets',
    defaultMessage: 'Rule sets'
  },
  norulesets: {
    id: 'rulesets.norulesets',
    defaultMessage: 'No rule sets'
  },
  number_of_rules: {
    id: 'rulesets.number_of_rules',
    defaultMessage: 'Number of rules'
  },
  fire_count: {
    id: 'rulesets.fire_count',
    defaultMessage: 'Fire count'
  },
  deleteRuleSetTitle: {
    id: 'rulesets.deleteRuleSet',
    defaultMessage: 'Delete rule set'
  },
  backToRuleSets: {
    id: 'ruleset.backToRuleSets',
    defaultMessage: 'Back to Rule Sets'
  },
  norulesetrules: {
    id: 'ruleset.norulesetrules',
    defaultMessage: 'No rules for this rule set'
  },
  norulesetsources: {
    id: 'ruleset.norulesetsources',
    defaultMessage: 'No sources for this rule set'
  },
  noactivationjobs: {
    id: 'activation.nojobs_description',
    defaultMessage: 'There are currently no jobs for this rulebook activation.'
  },
  nojobs_description: {
    id: 'common.nojobs_description',
    defaultMessage: 'There are currently no jobs for your organization.'
  },
  nojobs_action: {
    id: 'common.nojobs_action',
    defaultMessage: 'Please add a job by using the button below.'
  },
  lastFiredDate: {
    id: 'activation.lastFiredDate',
    defaultMessage: 'Last fired date'
  },
  executionEnvironmentPlaceholder: {
    id: 'activation.executionEnvironmentPlaceholder',
    defaultMessage: 'Select an Execution Environment URL'
  },
  restartPolicyPlaceholder: {
    id: 'activation.restartPolicyPlaceholder',
    defaultMessage: 'Select a Restart policy'
  },
  inventoryPlaceholder: {
    id: 'activation.inventoryPlaceholder',
    defaultMessage: 'Select an Inventory'
  },
  playbookPlaceholder: {
    id: 'activation.playbookPlaceholder',
    defaultMessage: 'Select a Playbook'
  },
  ruleBookPlaceholder: {
    id: 'activation.ruleBookPlaceholder',
    defaultMessage: 'Select a Rulebook'
  },
  backToRulebookActivations: {
    id: 'activation.backToRulebookActivations',
    defaultMessage: 'Back to Rulebook Activations'
  },
  extraVarPlaceholder: {
    id: 'project.extraVarPlaceholder',
    defaultMessage: 'Select Extra variables'
  },
  action: {
    id: 'rule.action',
    defaultMessage: 'Action'
  },
  condition: {
    id: 'rule.condition',
    defaultMessage: 'Condition'
  },
  backToRules: {
    id: 'rule.backToRules',
    defaultMessage: 'Back to Rules'
  },
  workingDirectory: {
    id: 'shared.workingDirectory',
    defaultMessage: 'Working directory'
  },
  workingDirectoryPlaceholder: {
    id: 'shared.workingDirectoryPlaceholder',
    defaultMessage: 'Working directory'
  },
  enterRulebookActivationWorkingDirectory: {
    id: 'activation.enterRulebookActivationWorkingDirectory',
    defaultMessage: 'Enter a rulebook working directory'
  },
  backToRuleBooks: {
    id: 'rulebook.backToRuleBooks',
    defaultMessage: 'Back to Rulebooks'
  },
  rulebooks: {
    id: 'rulebook.rulebooks',
    defaultMessage: 'Rulebooks'
  },
  rulebook: {
    id: 'rulebook.rulebook',
    defaultMessage: 'Rulebook'
  },
  norulebooks: {
    id: 'rulebook.norulebooks',
    defaultMessage: 'There are currently no rulebooks for your organization'
  },
  norulebookrulesets: {
    id: 'rulebook.norulebookrulesets',
    defaultMessage: 'No rule sets for this rulebook'
  },
  number_of_rulesets: {
    id: 'rulebook.number_of_ruesets',
    defaultMessage: 'Number of rulesets'
  },
  jobRemoveTitle: {
    id: 'job.removeJob',
    defaultMessage: 'Delete job'
  },
  jobRemoveDescription: {
    id: 'job.removeJobDescription',
    defaultMessage: 'Are you sure you want to delete the job below?'
  },
  inventory: {
    id: 'inventory.inventory',
    defaultMessage: 'Inventory'
  },
  inventories: {
    id: 'inventory.inventories',
    defaultMessage: 'Inventories'
  },
  noinventories_action: {
    id: 'inventory.noinventories_action',
    defaultMessage: 'Please add an inventory by using the button below.'
  },
  noinventories_description: {
    id: 'inventory.noinventories_description',
    defaultMessage: 'There are currently no inventories added for your organization.'
  },
  add_new_inventory: {
    id: 'inventory.addNewInventory',
    defaultMessage: 'Add new inventory'
  },
  inventoryRemoveTitle: {
    id: 'inventory.removeInventory',
    defaultMessage: 'Delete inventory'
  },
  inventoryRemoveDescription: {
    id: 'inventory.removeInventoryDescription',
    defaultMessage: 'Are you sure you want to delete the inventory below?'
  },
  addInventory: {
    id: 'inventory.addInventory',
    defaultMessage: 'Add inventory'
  },
  deleteInventoryTitle: {
    id: 'inventory.deleteInventory',
    defaultMessage: 'Delete inventory'
  },
  backToInventories: {
    id: 'project.backToInventories',
    defaultMessage: 'Back to Inventories'
  },
  source_of_inventory: {
    id: 'inventory.source_of_inventory',
    defaultMessage: 'Source of inventory'
  },
  enterInventoryName: {
    id: 'inventory.enterInventoryName',
    defaultMessage: 'Enter an inventory name'
  },
  enterInventoryDescription: {
    id: 'inventory.enterInventoryDescription',
    defaultMessage: 'Enter an inventory description'
  }
});

export default sharedMessages;
