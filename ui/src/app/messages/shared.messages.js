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
  project: {
    id: 'project.project',
    defaultMessage: 'Project'
  },
  projects: {
    id: 'project.projects',
    defaultMessage: 'Projects'
  },
  noprojects: {
    id: 'project.noprojects',
    defaultMessage: 'No projects'
  },
  addProject: {
    id: 'project.addProject',
    defaultMessage: 'Add project'
  },
  deleteProjectTitle: {
    id: 'project.deleteProject',
    defaultMessage: 'Delete project'
  },
  activation: {
    id: 'activation.activation',
    defaultMessage: 'Activation'
  },
  activations: {
    id: 'activation.activations',
    defaultMessage: 'Rulebook activations'
  },
  noactivations: {
    id: 'activation.noactivations',
    defaultMessage: 'There are currently no rulebook activations added for your organization.'
  },
  addActivation: {
    id: 'activation.addActivation',
    defaultMessage: 'Add rulebook activation'
  },
  deleteActivationTitle: {
    id: 'activation.deleteActivation',
    defaultMessage: 'Delete activation'
  },
  enterRulebookActivationName: {
    id: 'activation.enterRulebookActivationName',
    defaultMessage: 'Enter a rulebook activation name'
  },
  selectRuleSet: {
    id: 'activation.selectRulebookActivationName',
    defaultMessage: 'Select a rule set'
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
  }
});

export default sharedMessages;
