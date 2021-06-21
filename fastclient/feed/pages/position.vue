<template>
  <div>
    <comba-table :url="url" :table="table"></comba-table>
  </div>
</template>

<script>
import CombaTable from '@/components/CombaTable/index';

const url = '/feed/object';
const table = 'u_loc_info';

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

