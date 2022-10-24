import {PageSection, Title, ToolbarGroup, ToolbarItem} from '@patternfly/react-core';
import {Link, Route, useHistory} from 'react-router-dom';
import React, {useState, useEffect, useReducer, Fragment} from 'react';
import { Button } from '@patternfly/react-core';
import {TopToolbar} from '../shared/top-toolbar';
import { PlusCircleIcon } from '@patternfly/react-icons';
import sharedMessages from '../messages/shared.messages';
import {cellWidth} from "@patternfly/react-table";
import ActivationsTableContext from './activations-table-context';
import {TableToolbarView} from "@app/shared/table-toolbar-view";
import TableEmptyState from "@app/shared/table-empty-state";
import {useIntl} from "react-intl";
import {defaultSettings} from "@app/shared/pagination";
import {NewActivation} from "@app/NewActivation/NewActivation";
import {createRows} from "@app/Activations/activations-table-helpers";
import {AnyObject} from "@app/shared/types/common-types";
import {RemoveActivation} from "@app/RemoveActivation/RemoveActivation";
import {listActivations} from "@app/API/Activation";

export interface ActivationType {
  id: string;
  name: string;
  description: string,
  extra_var_id?: string,
  execution_environment?: string,
  playbook?: string,
  restarted_count?: string,
  restart_policy?: string,
  last_restarted?: string,
  status?: string,
  ruleset_id?: string,
  ruleset_name?: string,
  inventory_id?: string,
  inventory_name?: string,
  number_of_rules?: string,
  fire_count?: string,
  created_at?: string,
  updated_at?: string
}

const columns = (intl) => [
  {
    title: (
      ''
    ),
    transforms: [cellWidth(10 )]
  },
  {
  title: (intl.formatMessage(sharedMessages.name))
  },
  {
    title: (intl.formatMessage(sharedMessages.activation_status))
  },
  {
    title: (intl.formatMessage(sharedMessages.number_of_rules))
  },
  {
    title: (intl.formatMessage(sharedMessages.fire_count))
  }
];

const prepareChips = (filterValue, intl) =>
  filterValue
    ? [
      {
        category: intl.formatMessage(sharedMessages.name),
        key: 'name',
        chips: [{ name: filterValue, value: filterValue }]
      }
    ]
    : [];

const initialState = (filterValue = '') => ({
  filterValue,
  isFetching: true,
  isFiltering: false,
  selectedActivations: [],
  selectedAll: false,
  rows: []
});

const areSelectedAll = (rows:ActivationType[] = [], selected) =>
  rows.every((row) => selected.includes(row.id));

const unique = (value, index, self) => self.indexOf(value) === index;

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const activationsListState = (state, action) => {
  switch (action.type) {
    case 'setRows':
      return {
        ...state,
        rows: action.payload,
        selectedAll: areSelectedAll(action.payload, state.selectedActivations)
      };
    case 'setFetching':
      return {
        ...state,
        isFetching: action.payload
      };
    case 'setFilterValue':
      return { ...state, filterValue: action.payload };
    case 'select':
      return {
        ...state,
        selectedAll: false,
        selectedActivations: state.selectedActivations.includes(action.payload)
          ? state.selectedActivations.filter((id) => id !== action.payload)
          : [...state.selectedActivations, action.payload]
      };
    case 'selectAll':
      return {
        ...state,
        selectedActivations: [
          ...state.selectedActivations,
          ...action.payload
        ].filter(unique),
        selectedAll: true
      };
    case 'unselectAll':
      return {
        ...state,
        selectedActivations: state.selectedActivations.filter(
          (selected) => !action.payload.includes(selected)
        ),
        selectedAll: false
      };
    case 'resetSelected':
      return {
        ...state,
        selectedActivations: [],
        selectedAll: false
      };
    case 'setFilteringFlag':
      return {
        ...state,
        isFiltering: action.payload
      };
    case 'clearFilters':
      return { ...state, filterValue: '', isFetching: true };
    default:
      return state;
  }
};

const Activations: React.FunctionComponent = () => {
  const intl = useIntl();
  const history = useHistory();
  const [activations, setActivations] = useState<ActivationType[]>([]);
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);

  const data = activations;
  const meta = {count: activations?.length || 0, limit, offset};
  const [
    {
      filterValue,
      isFetching,
      isFiltering,
      selectedActivations,
      selectedAll,
      rows
    },
    stateDispatch
  ] = useReducer(activationsListState, initialState());

  const setSelectedActivations = (ids: string[]) =>
    stateDispatch({type: 'select', payload: ids});

  const handlePagination = (pagination) => {
    stateDispatch({type: 'setFetching', payload: true});
    return listActivations(pagination).then(data => { setActivations(data); stateDispatch({type: 'setRows', payload: createRows(activations)});})
      .then(() => {stateDispatch({type: 'setFetching', payload: false});})
      .catch(() => stateDispatch({type: 'setFetching', payload: false}));
  };

  useEffect(() => {
    handlePagination(defaultSettings);
  }, []);

  useEffect(() => {
    stateDispatch({type: 'setRows', payload: createRows(activations)});
  }, [activations]);

  const clearFilters = () => {
    stateDispatch({type: 'clearFilters'});
    return handlePagination(meta);
  };

  const handleFilterChange = (value) => {
    !value || value === ''
      ? clearFilters()
      : stateDispatch({type: 'setFilterValue', payload: value});
  };

   const routes = () => <Fragment>
    <Route
      exact
      path={'/activations/new-activation'}
      render={(props: AnyObject) => (
        <NewActivation {...props} />
      )}
    />
    <Route exact path="/activations/remove/:id"
           render={ props => <RemoveActivation { ...props }
                                             fetchData={ handlePagination }
                                               resetSelectedActivations={() =>
                                                 stateDispatch({ type: 'resetSelected' })
                                               } /> }/>
    <Route exact path="/activations/remove"
           render={ props => <RemoveActivation { ...props }
                                             ids={ selectedActivations }
                                             fetchData={ handlePagination }
                                               resetSelectedActivations={() =>
                                                 stateDispatch({ type: 'resetSelected' })
                                               } /> }/>
  </Fragment>;


  const actionResolver = () => [
    {
      title: intl.formatMessage(sharedMessages.relaunch),
      component: 'button',
      onClick: (_event, _rowId, activation) =>
        history.push({
          pathname: `/activations/relaunch/${activation.id}`
        })
    },
    {
      title: intl.formatMessage(sharedMessages.restart),
      component: 'button',
      onClick: (_event, _rowId, activation) =>
        history.push({
          pathname: `/activations/restart/${activation.id}`
        })
    },
    {
      title: intl.formatMessage(sharedMessages.disable),
      component: 'button',
      onClick: (_event, _rowId, activation) =>
        history.push({
          pathname: `/activations/disable/${activation.id}`
        })
    },
    {
      title: intl.formatMessage(sharedMessages.delete),
      component: 'button',
      onClick: (_event, _rowId, activation) =>
        history.push({
          pathname: `/activations/remove/${activation.id}`
        })
    }
  ];

  const selectAllFunction = () =>
      stateDispatch({type: 'selectAll', payload: data.map((item) => item.id)});

  const unselectAllFunction = () =>
    stateDispatch({type: 'unselectAll', payload: data.map((item) => item.id)});

  const anyActivationsSelected = selectedActivations.length > 0;

  const bulkSelectProps = React.useMemo(() => {
    return {
      count: selectedActivations.length || 0,
      items: [
        {
          title: 'Select none (0)',
          onClick: unselectAllFunction
        },
        {
          title: `Select all (${activations.length || 0})`,
          onClick: selectAllFunction
        }
      ],
      checked: selectedActivations.length === activations.length,
      onSelect: (isChecked: boolean) => isChecked ? selectAllFunction() : unselectAllFunction()
    };
  }, [ selectedActivations.length, activations.length ]);

  const toolbarButtons = () => (
    <ToolbarGroup className={`pf-u-pl-lg top-toolbar`}>
      <ToolbarItem>
        <Link
          id="add-activation-link"
          to={{pathname: '/new-activation'}}
        >
          <Button
            ouiaId={'add-activation-link'}
            variant="primary"
            aria-label={intl.formatMessage(sharedMessages.addActivation)}
          >
            {intl.formatMessage(sharedMessages.addActivation)}
          </Button>
        </Link>
      </ToolbarItem>
      <ToolbarItem>
        <Link
          id="remove-multiple-activations"
          className={anyActivationsSelected ? '' : 'disabled-link'}
          to={{pathname: '/activations/remove'}}
        >
          <Button
            variant="secondary"
            isDisabled={!anyActivationsSelected}
            aria-label={intl.formatMessage(
              sharedMessages.deleteActivationTitle
            )}
          >
            {intl.formatMessage(sharedMessages.delete)}
          </Button>
        </Link>
      </ToolbarItem>
    </ToolbarGroup>
  );

  return (
    <Fragment>
      <TopToolbar>
        <Title headingLevel={"h2"}>{intl.formatMessage(sharedMessages.activations)}</Title>
      </TopToolbar>
      <ActivationsTableContext.Provider
        value={{
          selectedActivations,
          setSelectedActivations
        }}
      >
        <PageSection page-type={'activations-list'} id={'activations_list'}>
          <TableToolbarView
            ouiaId={'activations-table'}
            rows={rows}
            setLimit={setLimit}
            setOffset={setOffset}
            columns={columns(intl)}
            bulkSelect={bulkSelectProps}
            fetchData={handlePagination}
            routes={routes}
            actionResolver={actionResolver}
            plural={intl.formatMessage(sharedMessages.activations)}
            singular={intl.formatMessage(sharedMessages.activation)}
            toolbarButtons={toolbarButtons}
            isLoading={isFetching || isFiltering}
            onFilterChange={handleFilterChange}
            renderEmptyState={() => (
              <TableEmptyState
                title={intl.formatMessage(sharedMessages.noactivations_description)}
                Icon={PlusCircleIcon}
                PrimaryAction={() =>
                  filterValue !== '' ? (
                    <Button onClick={() => clearFilters()} variant="link">
                      {intl.formatMessage(sharedMessages.clearAllFilters)}
                    </Button>
                  ) : (
                    <Link
                      id="create-activation-link"
                      to={{pathname: '/new-activation'}}
                    >
                      <Button
                        ouiaId={'create-activation-link'}
                        variant="primary"
                        aria-label={intl.formatMessage(
                          sharedMessages.addActivation
                        )}
                      >
                        {intl.formatMessage(sharedMessages.addActivation)}
                      </Button>
                    </Link>
                  )
                }
                description={
                  filterValue === ''
                    ? intl.formatMessage(sharedMessages.noactivations_action)
                    : intl.formatMessage(
                    sharedMessages.clearAllFiltersDescription
                    )
                }
              />
            )}
          />
        </PageSection>
      </ActivationsTableContext.Provider>
    </Fragment>
  );
}
export { Activations };
