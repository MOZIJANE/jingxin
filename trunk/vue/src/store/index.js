import Vue from 'vue';
import Vuex, { Store } from 'vuex';
import createPersistedState from 'vuex-persistedstate';

import { getMenu } from '@/services';

import getters from './getters';
import mutations from './mutations';
import app from './modules/app';
import user from './modules/user';

Vue.use(Vuex);

export default new Store({
  modules: {
    app,
    user,
  },
  getters,
  mutations,
  state: {
    loading: false,
    port: 3000,
    auth: true,
    menu: [],
    sMenu: [],
    dateRangeType: '',
    dateRangeStart: new Date(),
    dateRangeEnd: new Date(),
  },
  actions: {
    async SetMenu({ commit }) {
      getMenu().then((response) => {
        commit('SET_MENU', response.pages);
        // commit('SHAPE_MENU', response.pages);
      });
    },
  },
  plugins: [createPersistedState({ storage: window.sessionStorage })],
});

