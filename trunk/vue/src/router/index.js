import Vue from 'vue';
import Router from 'vue-router';
import routes from './routes';

Vue.use(Router);

const registerRoutes = routes.map(({ key, component }) => {
  const keyArray = key.split('/');
  const name = keyArray.join('-').replace('-', '');
  let path = keyArray
    .map(item => (item.startsWith('_') ? item.replace('_', ':') : item))
    .join('/');
  if (key.endsWith('/index')) {
    path = path.replace('/index', '');
  }
  return {
    component,
    path,
    name,
    meta: {
      layout: component.layout || 'default',
      title: component.title,
    },
  };
});

export default new Router({
  // mode: 'history',
  routes: [...registerRoutes],
});
