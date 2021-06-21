<template>
  <div id="app">
    <component :is="$route.meta.layout" />
  </div>
</template>

<script>
import components from '@/layouts';

export default {
  name: 'App',
  components,
};
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
