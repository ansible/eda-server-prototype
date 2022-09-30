import React, { Suspense } from 'react';
import { RemoveProject } from './RemoveProject/RemoveProject';
import {Route, Switch} from "react-router-dom";

const DialogRoutes = () => (
  <Suspense fallback={<div></div>}>
    <Switch>
      <Route path="/projects/remove-project/:id">
        <RemoveProject />
      </Route>
    </Switch>
  </Suspense>
);

export default DialogRoutes;
