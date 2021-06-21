// Use require.context to require reducers automatically
// Ref: https://webpack.js.org/guides/dependency-management/#require-context
const context = require.context('./', false, /\.(js|vue)$/);
const components = {};
const array = context
  .keys()
  .map(key => ({ key: key.split('.')[1].split('/')[1], component: context(key).default || context(key) }));

array.forEach(({ key, component }) => { components[key] = component; });

export default components;
