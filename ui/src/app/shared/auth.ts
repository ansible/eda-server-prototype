import {getServer} from "@app/utils/utils";

export const loginUser = (loginData) => {
  return fetch('http://' + getServer() + '/api/auth/jwt/login',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
      },
      body: loginData
    }
  )
};

export const getUser = () => {
  return fetch('http://' + getServer() + '/api/users/me',
    {
      method: 'GET',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
      }
    }
  )
};

export const logoutUser = () => {
  return fetch('http://' + getServer() + '/api/auth/jwt/logout',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
      }
    }
  )
};
