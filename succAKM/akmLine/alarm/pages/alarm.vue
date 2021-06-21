<template>
    <el-row :gutter="16" class="el-row">
      <el-col :span="24">
        <el-tabs type="border-card" v-model="label">
          <el-tab-pane label="活动告警">
            <comba-picker-table
              v-if="label === '0'"
              :url="api"
              :table="activeTable"
              style="min-height: 840px; line-height: .6rem;"
            ></comba-picker-table>
          </el-tab-pane>
          <el-tab-pane label="历史告警">
            <comba-picker-table
              v-if="label === '1'"
              :url="api"
              :table="activeTable"
              style="min-height: 840px; line-height: .6rem;"
            ></comba-picker-table>
          </el-tab-pane>
        </el-tabs>
      </el-col>
    </el-row>
</template>

<script>
import CombaPickerTable from '@/components/CombaPicker/Table';

const url = '/alarm/bigtable';

export default {
  name: 'platform-alarm',
  layout: 'platform',
  components: {
    CombaPickerTable,
  },
  data() {
    return {
      api: url,
      label: '0',
    };
  },
  computed: {
    activeTable() {
      const { label } = this;
      if (label === '0') {
        return 'r_alarm';
      }
      return 'r_alarm_history';
    },
  },
};
</script>
