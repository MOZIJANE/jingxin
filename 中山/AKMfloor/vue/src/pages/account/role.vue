<template>
  <div>
    <comba-table :url="url" :table="table"></comba-table>
  </div>
</template>

<script>
import CombaTable from '@/components/CombaTable/index';

const url = '/account/object';
const table = 'u_role';

export default {
  layout: 'platform',
  components: {
    CombaTable,
  },
  data() {
    return {
      url,
      table,
    };
  },
};
</script>

<style lang="scss" scoped>
</style>

