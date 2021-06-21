<template>
    <el-row :gutter="16" class="el-row">
      <el-col :span="24">
        <el-row class="el-row">
          <comba-picker-table
            :url="api"
            table="u_agv_task"
            style="min-height: 840px; line-height: .6rem;"
          ></comba-picker-table>
        </el-row>
      </el-col>
    </el-row>
</template>

<script>
import CombaPickerTable from '@/components/CombaPicker/Table';

const url = '/agvCtrl/bigtable';
export default {
  name: 'platform-test',
  layout: 'platform',
  components: {
    CombaPickerTable,
  },
  data() {
    return {
      api: url,
    };
  },
};
</script>
