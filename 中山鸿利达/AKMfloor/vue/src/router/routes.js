// Use require.context to require reducers automatically
// Ref: https://webpack.js.org/guides/dependency-management/#require-context
const context = require.context('../pages/', true, /\.vue$/);
export default context
  .keys()
  .map(key => ({ key: key.split('.')[1], component: context(key).default || context(key) }));

