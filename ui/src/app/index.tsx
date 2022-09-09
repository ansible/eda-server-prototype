import * as React from 'react';
import { Route, Switch } from 'react-router-dom';
import { IntlProvider } from 'react-intl';
import '@patternfly/react-core/dist/styles/base.css';
import { BrowserRouter as Router } from 'react-router-dom';
import { AppLayout } from '@app/AppLayout/AppLayout';
import { AppRoutes } from '@app/routes';
import '@app/app.css';
import GlobalStyle from '../global-styles';

const App: React.FunctionComponent = () => (
  <React.Fragment>
  <GlobalStyle />
    <IntlProvider locale="en">
    <Router basename='/'>
      <Switch>
        <Route>
          <AppLayout>
            <AppRoutes />
          </AppLayout>
        </Route>
        </Switch>
      </Router>
    </IntlProvider>
  </React.Fragment>
);

export default App;
