import { Card, CardBody, CardFooter, CardTitle, Level, LevelItem, Title } from '@patternfly/react-core';
import { Link, useHistory } from 'react-router-dom';
import React, { useState, useEffect, useReducer, Fragment } from 'react';
import { Button } from '@patternfly/react-core';
import { PlusCircleIcon } from '@patternfly/react-icons';
import sharedMessages from '../messages/shared.messages';
import { TableToolbarView } from '@app/shared/table-toolbar-view';
import TableEmptyState from '@app/shared/table-empty-state';
import { useIntl } from 'react-intl';
import { defaultSettings } from '@app/shared/pagination';
import { listProjects } from '@app/API/Project';

interface ProjectCardType {
  id: string;
  name: string;
  status?: string;
  revision?: string;
}

const createRows = (data: ProjectCardType[]) =>
  data.slice(-4).map(({ id, name, status, revision }) => ({
    id,
    cells: [
      <Fragment key={`[project-${id}`}>
        <Link
          to={{
            pathname: `/project/${id}`,
          }}
        >
          {name}
        </Link>
      </Fragment>,
      status,
      revision || '000000',
    ],
  }));

const columns = (intl) => [
  {
    title: intl.formatMessage(sharedMessages.name),
  },
  {
    title: intl.formatMessage(sharedMessages.status),
  },

  {
    title: intl.formatMessage(sharedMessages.revision),
  },
];

const initialState = () => ({
  isFetching: true,
  rows: [],
});

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const projectsListState = (state, action) => {
  switch (action.type) {
    case 'setRows':
      return {
        ...state,
        rows: action.payload,
      };
    case 'setFetching':
      return {
        ...state,
        isFetching: action.payload,
      };
    default:
      return state;
  }
};

const ProjectsCard: React.FunctionComponent = () => {
  const intl = useIntl();
  const [projects, setProjects] = useState<ProjectCardType[]>([]);
  const [limit, setLimit] = useState(defaultSettings.limit);
  const [offset, setOffset] = useState(1);
  const [{ isFetching, rows }, stateDispatch] = useReducer(projectsListState, initialState());
  const history = useHistory();

  const updateRows = () => {
    stateDispatch({ type: 'setFetching', payload: true });
    return listProjects()
      .then((data) => {
        setProjects(data?.data);
        stateDispatch({ type: 'setRows', payload: createRows(projects) });
      })
      .then(() => {
        stateDispatch({ type: 'setFetching', payload: false });
      })
      .catch(() => stateDispatch({ type: 'setFetching', payload: false }));
  };

  useEffect(() => {
    updateRows();
  }, []);

  useEffect(() => {
    stateDispatch({ type: 'setRows', payload: createRows(projects) });
  }, [projects]);

  return (
    <Fragment>
      <Card style={{ transition: 'box-shadow 0.25s', minHeight: 575 }}>
        <CardTitle>
          <Level>
            <LevelItem>
              <Title headingLevel={'h2'}>{intl.formatMessage(sharedMessages.projects)}</Title>
            </LevelItem>
            <LevelItem>
              <Button variant="link" onClick={() => history.push('/projects')}>
                {intl.formatMessage(sharedMessages.go_to_projects)}
              </Button>
            </LevelItem>
          </Level>
        </CardTitle>
        <CardBody>
          <TableToolbarView
            ouiaId={'projects-table'}
            rows={rows}
            setLimit={setLimit}
            setOffset={setOffset}
            columns={columns(intl)}
            fetchData={updateRows}
            plural={intl.formatMessage(sharedMessages.projects)}
            singular={intl.formatMessage(sharedMessages.project)}
            isLoading={isFetching}
            renderEmptyState={() => (
              <TableEmptyState
                title={intl.formatMessage(sharedMessages.noprojects_description)}
                Icon={PlusCircleIcon}
                PrimaryAction={() => (
                  <Link id="create-project-link" to={{ pathname: '/new-project' }}>
                    <Button
                      ouiaId={'create-project-link'}
                      variant="primary"
                      aria-label={intl.formatMessage(sharedMessages.addProject)}
                    >
                      {intl.formatMessage(sharedMessages.addProject)}
                    </Button>
                  </Link>
                )}
                description={intl.formatMessage(sharedMessages.noprojects_action)}
              />
            )}
          />
        </CardBody>
        <CardFooter>
          <Button variant="link" icon={<PlusCircleIcon />} onClick={() => history.push('/new-project')}>
            {intl.formatMessage(sharedMessages.create_project)}
          </Button>
        </CardFooter>
      </Card>
    </Fragment>
  );
};
export { ProjectsCard };
