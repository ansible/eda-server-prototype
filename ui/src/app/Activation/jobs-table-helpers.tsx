import React, { Fragment, useContext } from 'react';
import {Link} from "react-router-dom";

export const createRows = (data) =>
  data.map(({ job_instance_id, name, status, rule, last_fired_at }) => ({
    job_instance_id,
    cells: [
      <Fragment key={`[job-${job_instance_id}`}>
        <Link
          to={{
            pathname: `/job/${job_instance_id}`
          }}
        >
          {name || job_instance_id}
        </Link>
      </Fragment>,
      status,
      rule,
      last_fired_at
    ]
  }));
