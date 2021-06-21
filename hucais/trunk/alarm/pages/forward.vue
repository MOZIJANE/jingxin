<template>
  <div>
    <comba-table :url="url" :table="table"></comba-table>
  </div>
</template>

<script>
import CombaTable from '@/components/CombaTable/index';

const url = '/alarm/object';
const table = 'u_alarm_forward';

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

