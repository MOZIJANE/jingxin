<template>
  <div>
    <comba-table :url="url" :table="table"></comba-table>
  </div>
</template>

<script>
import CombaTable from '@/components/CombaTable/index';

const url = '/agvctrl/ironarm';
const table = 'u_scada_position';

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

