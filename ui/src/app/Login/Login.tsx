import React, { useState } from 'react';
import {
  LoginForm,
  LoginPage,
} from '@patternfly/react-core';
import ExclamationCircleIcon from '@patternfly/react-icons/dist/esm/icons/exclamation-circle-icon';
import { useHistory } from 'react-router-dom';
import { getServer } from '@app/utils/utils';
import Logo from '../../assets/images/logo-masthead.svg';

function Login(props) {

    const history = useHistory();

    const [showHelperText, setShowHelperText] = useState(false);
    const [usernameValue, setUsernameValue] = useState('');
    const [isValidUsername, setIsValidUsername] = useState(true);
    const [passwordValue, setPasswordValue] = useState('');
    const [isValidPassword, setIsValidPassword] = useState(true);

    const handleUsernameChange = value => {
      setUsernameValue(value);
    };

    const handlePasswordChange = passwordValue => {
      setPasswordValue(passwordValue);
    };

    const onLoginButtonClick = event => {
      event.preventDefault();
      setIsValidUsername(!!usernameValue);
      setIsValidPassword(!!passwordValue);
      setShowHelperText(!usernameValue || !passwordValue);
      if (!!usernameValue && !!passwordValue) {

				const details = {
					'username': usernameValue,
					'password': passwordValue,
				};

				let formBody = [];
				for (const property in details) {
					const encodedKey = encodeURIComponent(property);
					const encodedValue = encodeURIComponent(details[property]);
					formBody.push(encodedKey + "=" + encodedValue);
				}
				formBody = formBody.join("&");
				fetch('http://' + getServer() + '/api/auth/jwt/login',
						{
							method: 'POST',
							headers: {
								'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
							},
							body: formBody
						}
				).then((response) => {
          if(!response.ok) {
            setIsValidUsername(false);
            setIsValidPassword(false);
            setShowHelperText(true);
          } else {
            history.push('/dashboard');
          }
        });
      }
    };

    const helperText = (
      <React.Fragment>
        <ExclamationCircleIcon />
        &nbsp;Invalid login credentials.
      </React.Fragment>
    );

    const loginForm = (
      <LoginForm
        showHelperText={showHelperText}
        helperText={helperText}
        helperTextIcon={<ExclamationCircleIcon />}
        usernameLabel="Username"
        usernameValue={usernameValue}
        onChangeUsername={handleUsernameChange}
        isValidUsername={isValidUsername}
        passwordLabel="Password"
        passwordValue={passwordValue}
        onChangePassword={handlePasswordChange}
        isValidPassword={isValidPassword}
        onLoginButtonClick={onLoginButtonClick}
        loginButtonLabel="Log in"
      />
    );

    const images = {
      lg: '/assets/images/pfbg_2000.jpg',
      sm: '/assets/images/pfbg_768.jpg',
      sm2x: '/assets/images/pfbg_768@2x.jpg',
      xs: '/assets/images/pfbg_576.jpg',
      xs2x: '/assets/images/pfbg_576@2x.jpg'
    };

    return (
      <LoginPage
        brandImgAlt="Ansible Platform"
        style={{
          backgroundColor: 'var(--pf-global--BackgroundColor--dark-100)',
        }}
        backgroundImgAlt="Images"
        brandImgSrc={Logo}
        loginTitle="Log in to your account"
        loginSubtitle="Enter your sign-on credentials."
      >
        {loginForm}
      </LoginPage>
    );
}

export { Login };
