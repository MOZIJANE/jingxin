<template>
  <div>
    <el-card>
      <div style="padding: 6px 0 20px;">
        <el-row>
          <el-col :span="24">
            <comba-picker-base
              :apis="apis"
              @response-received="handleResponseReceived">
            </comba-picker-base>
          </el-col>
        </el-row>

      </div>

      <div class="chart-wrapper">
        <el-row :gutter="16">
          <el-col :span="12">
            <chart-card
              key="test"
              ref="test"
              title=""
              :options="rangeData.test"
            ></chart-card>
          </el-col>
          <el-col :span="12">
            <chart-card
              key="test2"
              ref="test2"
              title=""
              :options="rangeData.test2"
            ></chart-card>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <el-row class="mt3">
      <comba-picker-table
        :url="bigTable"
        table="r_log_critical"
        style="min-height: 840px; line-height: .6rem;"
      ></comba-picker-table>
    </el-row>

  </div>
</template>

<script>
import CombaPickerBase from '@/components/CombaPicker/Base';
import ChartCard from '@/components/ECharts/ChartCard';
import CombaPickerTable from '@/components/CombaPicker/TableBase';

const chartApi = '/rlog/logBar';
const chartApi2 = '/rlog/logPie';
const bigTable = '/rlog/bigtable';

export default {
  layout: 'platform',
  components: {
    CombaPickerBase,
    ChartCard,
    CombaPickerTable,
  },
  data() {
    return {
      bigTable,
      rangeData: {
        test: {},
        test2: {},
      },
      apis: [
        { ref: 'test', url: chartApi, data: {} },
        { ref: 'test2', url: chartApi2, data: { test: 'test' } },
      ],
    };
  },
  methods: {
    handleResponseReceived(data) {
      const { ref, response } = data;
      const { rangeData } = this;
      rangeData[ref] = response.options;
    },
  },
};
</script>

<style lang="scss" scoped>
.chart-wrapper {
  width: 100%;
  min-width: 600px;
}
.mt3 {
  margin-top: 16px;
}
</style>

