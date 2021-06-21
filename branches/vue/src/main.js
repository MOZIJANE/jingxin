// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue';
import VueAMap from 'vue-amap';
import Icon from 'vue-awesome/components/Icon';
import ElementUI from 'element-ui';
import VTooltip from 'v-tooltip';
import '@/element-variables.scss';
import App from '@/App';
import router from '@/router';
import store from '@/store';

Vue.config.productionTip = false;

Vue.use(VueAMap);
Vue.use(ElementUI);
Vue.use(VTooltip);

Vue.component('icon', Icon);

VueAMap.initAMapApiLoader({
  key: 'f66ff04b743a9b79a8bdb8c44879ca47',
  plugin: ['AMap.Scale', 'AMap.OverView', 'AMap.ToolBar', 'AMap.MapType'],
  v: '1.4.4',
});

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  render: h => h(App),
});

router.afterEach(() => {
  const { title } = router.app.$route.meta;
  document.title = !title ? '兴森快捷' : title;
});
