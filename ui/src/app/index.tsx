import * as React from 'react';
import { Route, Switch } from 'react-router-dom';
import '@patternfly/react-core/dist/styles/base.css';
import { BrowserRouter as Router } from 'react-router-dom';
import { AppLayout } from '@app/AppLayout/AppLayout';
import { AppRoutes } from '@app/routes';
import { Login } from '@app/Login/Login';
import '@app/app.css';

const App: React.FunctionComponent = () => (
  <Router basename="/eda">
    <Switch>
    <Route path="/" exact="true">
       <Login />
    </Route>
    <Route>
    <AppLayout>
      <AppRoutes />
    </AppLayout>
    </Route>
    </Switch>
  </Router>
);

export default App;
