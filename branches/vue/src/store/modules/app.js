import Cookies from 'js-cookie';

const app = {
  state: {
    activeMenuIndex: '',
    sidebar: {
      opened: !+Cookies.get('sidebarStatus'),
    },
  },
  mutations: {
    SET_ACTIVEMENUINDEX: (state, payload) => {
      state.activeMenuIndex = payload;
    },
    TOGGLE_SIDEBAR: (state) => {
      if (state.sidebar.opened) {
        Cookies.set('sidebarStatus', 1);
      } else {
        Cookies.set('sidebarStatus', 0);
      }
      state.sidebar.opened = !state.sidebar.opened;
    },
    OPEN_SIDEBAR: (state) => {
      state.sidebar.opened = true;
    },
    CLOSE_SIDEBAR: (state) => {
      state.sidebar.opened = false;
    },
  },
  actions: {
    ToggleSideBar: ({
      commit,
    }) => {
      commit('TOGGLE_SIDEBAR');
    },
  },
};

export default app;
