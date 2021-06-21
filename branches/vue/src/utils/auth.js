import Cookies from 'js-cookie';

const TokenKey = 'Session';

export function getToken() {
  return Cookies.get(TokenKey);
}

export function setToken(token) {
  return Cookies.set(TokenKey, token);
}

export function removeToken() {
  return Cookies.get(TokenKey) && Cookies.remove(TokenKey);
}
