import { login, logout, getInfo } from '@/services';
import { getToken, setToken, removeToken } from '@/utils/auth';
import router from '@/router';

export default {
  state: {
    token: getToken(),
    user: '',
    name: '',
    avatar: '',
    roles: [],
    domain: 'comba',
  },

  mutations: {
    SET_TOKEN: (state, token) => {
      state.token = token;
    },
    SET_USER: (state, payload) => {
      state.user = payload;
    },
    SET_NAME: (state, name) => {
      state.name = name;
    },
    SET_AVATAR: (state, avatar) => {
      state.avatar = avatar;
    },
    SET_ROLES: (state, roles) => {
      state.roles = roles;
    },
    SET_DOMAIN: (state, domain) => {
      state.domain = domain;
    },
  },

  actions: {
    // 登录
    Login({ commit, dispatch }, { domain, user, password }) {
      return new Promise((resolve, reject) => {
        login(domain, user.trim(), password)
          .then((response) => {
            const { name, session } = response;
            setToken(session);
            // alert(session);
            commit('SET_DOMAIN', domain);
            commit('SET_TOKEN', session);
            commit('SET_NAME', name);
            commit('SET_USER', user.trim());
            commit('SET_AUTH', true);
            // window.location.reload(); // to fix bug
            resolve(session);
          })
          .then(() => {
            dispatch('ToDashboard', { user });
          })
          .catch((error) => {
            reject(error);
          })
          .finally(() => {
            commit('TOGGLE_LOADING');
          });
      });
    },
    ToDashboard(_, { user }) {
      router.push({
        path: '/feed/trajectory',
        query: { user },
      });
    },

    // 获取用户信息
    GetInfo({ state }) {
      return new Promise((resolve, reject) => {
        getInfo(state.user)
          .then(response => resolve(response))
          .catch(error => reject(error));
      });
    },

    // 登出
    LogOut({ commit, state }) {
      return new Promise((resolve, reject) => {
        logout(state.token)
          .then(() => {
            commit('SET_TOKEN', '');
            commit('SET_ROLES', []);
            removeToken();
            resolve();
          })
          .catch((error) => {
            reject(error);
          })
          .finally(() => router.replace('/user/login'));
      });
    },

    // 前端 登出
    FedLogOut() {
      return new Promise((resolve) => {
        router.replace('/');
        // commit('SET_TOKEN', '');
        // removeToken();
        resolve();
      });
    },
  },
};

