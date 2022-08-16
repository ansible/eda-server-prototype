import React, { Fragment } from 'react';
import {Link} from "react-router-dom";
import {ProjectType} from "@app/shared/types/common-types";

export const createRows = (data: ProjectType[]) =>
  data.map(({ id, url, status, type, revision }) => ({
    id,
    cells: [
      <Fragment key={`[project-${id}`}>
        <Link
          to={{
            pathname: `/project/${id}`
          }}
        >
          {url}
        </Link>
      </Fragment>,
      status,
      type,
      revision
    ]
  }));
