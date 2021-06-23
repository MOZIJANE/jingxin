
const mutations = {
  SET_PORT: (state, payload) => {
    state.port = payload;
  },
  SET_AUTH: (state, payload) => {
    state.auth = payload;
  },
  SET_MENU: (state, payload) => {
    state.menu = payload;
  },
  TOGGLE_LOADING: (state) => {
    state.loading = !state.loading;
  },
  UPDATE_DATERANGETYPE: (state, payload) => {
    state.dateRangeType = payload;
  },
  UPDATE_DATERANGESTART: (state, payload) => {
    state.dateRangeStart = payload;
  },
  UPDATE_DATERANGEEND: (state, payload) => {
    state.dateRangeEnd = payload;
  },
};

export default mutations;
