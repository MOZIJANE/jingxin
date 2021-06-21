<template>
  <div class="icon bell">
    <el-popover
      popper-class="el-popover-notifications"
      width="260"
      trigger="click"
    >
      <div class="alarm-title">{{info.label}}</div>
      <el-table v-if="hasAlarm" style="width: 100%" :show-header="false" :data="alarms" v-loading="loading">
        <el-table-column prop="moid"></el-table-column>
        <el-table-column prop="type"></el-table-column>
        <el-table-column prop="desc"></el-table-column>
      </el-table>
      <div v-else>无</div>
      <el-badge slot="reference" :value="count" :max="100" class="el-badge" @click.native="fetchAlarmInfo">
        <div style="display: flex;flex-direction: row">
          <span style="padding-right: 5px">{{info.label}}</span>
          <icon :name="info.name" :color="info.color"></icon>
        </div>
      </el-badge>
    </el-popover>
  </div>
</template>

<script>
import { getAlarmInfo } from '@/services';

export default {
  name: 'navbar-alarm',
  props: {
    level: {
      type: String,
    },
    count: {
      type: Number,
    },
  },
  data() {
    return {
      loading: false,
      alarms: [],
    };
  },
  computed: {
    hasAlarm() {
      return this.alarms.length !== 0;
    },
    info() {
      const { level } = this;
      if (level === 'warning') {
        return { label: '提示告警', color: 'purple', name: 'info-circle' };
      }
      if (level === 'minor') {
        return { label: '次要告警', color: 'yellow', name: 'exclamation-triangle' };
      }
      if (level === 'major') {
        return { label: '主要告警', color: 'orange', name: 'exclamation-triangle' };
      }
      return { label: '紧急告警', color: 'red', name: 'exclamation-triangle' };
    },
  },
  methods: {
    fetchAlarmInfo() {
      this.loading = true;
      getAlarmInfo(this.level)
        .then((res) => {
          const { data: { alarms } } = res;
          this.alarms = alarms;
          this.loading = false;
        });
    },
  },
};
</script>

<style lang="scss" scoped>
.alarm-title {
  text-align: center;
  font-size: 1rem;
  width: 100%;
  padding-bottom: 4px;
  border-bottom: 1px solid #ddd;
}
</style>

