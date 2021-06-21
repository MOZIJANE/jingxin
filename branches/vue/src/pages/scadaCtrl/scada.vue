<template>
  <div>
    <el-tabs type="border-card">
      <el-tab-pane v-for="{table, label} in tables" :key="table" :label="label">
        <comba-table :url="url" :table="table" style="textAlign: left"></comba-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import CombaTable from '@/components/CombaTable/index';

const url = '/scadaCtrl/object';

export default {
  layout: 'platform',
  components: {
    CombaTable,
  },
  data() {
    return {
      url,
      tables: [
        { table: 'u_bin_position', label: 'BIN区位置管理' },
        { table: 'u_cnc_position', label: 'CNC区位置管理' },
        { table: 'u_product_position', label: '成品区位置管理' },
        { table: 'u_raw_position', label: '原料区位置管理' },
      ],
    };
  },
};
</script>

