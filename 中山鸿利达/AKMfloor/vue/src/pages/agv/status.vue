<template>
  <div>
    <el-row :gutter="16" class="mb3">
      <el-col :span="24">
        <el-card>
          <el-row>
            <h3 class="sub-title">AGV操作</h3>
          </el-row>
          <el-row>
            <el-button plain style="border-color:#cccccc;width:80px" onMouseOver="this.style.color='dodgerblue'"  onMouseOut="this.style.color='#606266'" @click="triggerGoHome($route.query.agvId)">返航</el-button>
            <el-button plain style="border-color:#cccccc;width:80px" onMouseOver="this.style.color='dodgerblue'"  onMouseOut="this.style.color='#606266'" @click="triggerUnlock($route.query.agvId)">解锁</el-button>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="16" class="mb3">
      <el-col :span="24">
        <el-card>
          <el-row>
            <comba-picker-base
              :apis="apis"
              @response-received="handleResponseReceived">
            </comba-picker-base>
          </el-row>
          <el-row :gutter="16" style="margin-top: 30px">
            <el-col :span="12">
              <chart-card
                key="battery"
                ref="battery"
                title=""
                :options="rangeData.battery"
              ></chart-card>
            </el-col>
            <el-col :span="12">
              <chart-card
                key="confidence"
                ref="confidence"
                title=""
                :options="rangeData.confidence"
              ></chart-card>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
    <el-row class="mb3">
      <el-card class="app-content app-content-status">
        <div class="row column">
          <h3 class="sub-title">状态信息</h3>
            <el-table
              :data="tableData"
              size="mini"
              :span-method="arraySpanMethod"
              style="width: 100%;float: left">
              <template v-for="col in columns">
                <el-table-column
                  v-if="col.prop === 'value'||col.prop === 'value_1'"
                  :key="col.prop"
                  :label="col.label"
                  :width="col.width">
                  <template slot-scope="scope">
                    <div v-if="col.prop === 'value'">
                      <div v-if="isSpecialField(scope.row.fieldId)">
                        <template v-for="(item, index) in [].concat(scope.row.value)">
                          <el-button :key="index" v-if="item" type="success" circle size="mini"></el-button>
                          <el-button :key="index" v-else type="info" circle size="mini"></el-button>
                        </template>
                      </div>
                      <div v-else-if="isEmergency(scope.row.fieldId)">
                        <el-button v-if="scope.row.value" type="danger" circle size="mini"></el-button>
                        <el-button v-else type="info" circle size="mini"></el-button>
                      </div>
                      <!-- <div v-else-if="isChargeField(scope.row.fieldId)">
                        <template v-if="scope.row.value">
                          <icon label="charging">
                            <icon name="battery-quarter" scale="2"  color="green"></icon>
                            <icon name="bolt" color="green"></icon>
                          </icon>
                          <span>充电中</span>
                        </template>
                        <template v-else>
                          <icon name="battery-half"></icon>
                        </template>
                      </div> -->
                      <span v-else>{{ scope.row.value }}</span>
                    </div>
                    <div v-else>
                      <div v-if="isSpecialField(scope.row.fieldId_1)">
                        <template v-for="(item, index) in [].concat(scope.row.value_1)">
                          <el-button :key="index" v-if="item" type="success" circle size="mini"></el-button>
                          <el-button :key="index" v-else type="info" circle size="mini"></el-button>
                        </template>
                      </div>
                      <div v-else-if="isEmergency(scope.row.fieldId_1)">
                        <el-button v-if="scope.row.value_1" type="danger" circle size="mini"></el-button>
                        <el-button v-else type="info" circle size="mini"></el-button>
                      </div>
                      <!-- <div v-else-if="isChargeField(scope.row.fieldId)">
                        <template v-if="scope.row.value">
                          <icon label="charging">
                            <icon name="battery-quarter" scale="2"  color="green"></icon>
                            <icon name="bolt" color="green"></icon>
                          </icon>
                          <span>充电中</span>
                        </template>
                        <template v-else>
                          <icon name="battery-half"></icon>
                        </template>
                      </div> -->
                      <span v-else>{{ scope.row.value_1 }}</span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column
                  v-else
                  :key="col.prop"
                  :prop="col.prop"
                  :label="col.label"
                  :width="col.width">
                </el-table-column>
              </template>
            </el-table>
        </div>
      </el-card>
    </el-row>
  </div>
</template>

<script>
import { getAgvStatus, agvGoHome, agvUnlock, resetBasket } from '@/services';
import CombaPickerBase from '@/components/CombaPicker/Base';
import ChartCard from '@/components/ECharts/ChartCard';
import ElCol from 'element-ui/packages/col/src/col';

const chartApi = '/agv/battery';
const chartApi2 = '/agv/confidence';

export default {
  layout: 'platform',
  name: 'agv-status',
  components: {
    ElCol,
    CombaPickerBase,
    ChartCard,
  },
  data() {
    return {
      avgID: '',
      columns: [
        { prop: 'name', label: '名字', width: 300 },
        { prop: 'value', label: '数值' },
        { prop: 'name_1', label: '名字', width: 300 },
        { prop: 'value_1', label: '数值' },
      ],
      tableData: [],
      rangeData: {
        battery: {},
        confidence: {},
      },
      apis: [
        { ref: 'battery', url: chartApi, data: { agv: this.$route.query.agvId } },
        { ref: 'confidence', url: chartApi2, data: { agv: this.$route.query.agvId } },
      ],
    };
  },
  computed: {
    dateRangeLastSec() {
      const { radio } = this;
      let ret;
      if (radio === '1分') {
        ret = 60;
      } else if (radio === '5分') {
        ret = 60 * 5;
      } else if (radio === '30分') {
        ret = 60 * 30;
      } else if (radio === '1小时') {
        ret = 60 * 60;
      } else if (radio === '3小时') {
        ret = 60 * 60 * 3;
      } else if (radio === '1天') {
        ret = 60 * 60 * 24;
      }
      return ret;
    },
  },
  methods: {
    handleResponseReceived(data) {
      const { ref, response } = data;
      const { rangeData } = this;
      rangeData[ref] = response.options;
    },
    arraySpanMethod({ row, columnIndex }) {
      if (row.isArrary) {
        if (columnIndex === 1) {
          return [1, 3];
        }
      }
      return {
        rowspan: 1,
        colspan: 1,
      };
    },
    triggerGoHome(agvId) {
      agvGoHome(agvId)
        .then(() => (this.$message.success(`${agvId} 返回原点请求成功!`)))
        .catch(() => (this.$message.error(`${agvId} 返回原点请求失败!`)));
    },
    triggerUnlock(agvId) {
      agvUnlock(agvId)
        .then(() => (this.$message.success(`${agvId} 解锁请求成功!`)))
        .catch(() => (this.$message.error(`${agvId} 解锁请求失败!`)));
    },
    setAllEmpty(agvId) {
      const basket = Array(12).fill('空筐');
      resetBasket({ agvId, basket })
        .then(() => (this.$message.success(`${agvId} 设置全部空筐请求成功!`)))
        .catch(() => (this.$message.error(`${agvId} 设置全部空筐请求失败!`)));
    },
    setAllNothing(agvId) {
      const basket = Array(12).fill('空位');
      resetBasket({ agvId, basket })
        .then(() => (this.$message.success(`${agvId} 设置全部空位请求成功!`)))
        .catch(() => (this.$message.error(`${agvId} 设置全部空位请求失败!`)));
    },
    updateStatus() {
      getAgvStatus(this.$route.query.agvId).then(({ data }) => {
        this.tableData = [];
        let fix = false;
        data.info.map((item, index) => {
          if (data.info[index].isArrary) {
            this.tableData.push(item);
          }
          if (data.info[index].isArrary !== true) {
            fix = !fix;
            if (fix) {
              this.tableData.unshift(item);
            } else {
              this.tableData[0] = {
                ...this.tableData[0],
                fieldId_1: item.fieldId,
                name_1: item.name,
                value_1: item.value,
              };
            }
          }
          return 0;
        });
      });
    },
    isSpecialField(field) {
      const specialFields = ['DI', 'DO', 'DI_valid'];
      if (specialFields.includes(field)) {
        return true;
      }
      return false;
    },
    isEmergency(field) {
      return field === 'emergency';
    },
    isChargeField(field) {
      return field === 'charging';
    },
  },
  mounted() {
    this.updateStatus();
    // eslint-disable-next-line
//    this.agvId=this.$route.query.agv;
    this.updateStatusInterval = setInterval(() => this.updateStatus(), 3000);
  },
  destroyed() {
    clearInterval(this.updateStatusInterval);
  },
};
</script>
<style lang="scss" scoped>
.mb3 {
margin-bottom: 16px;
}
</style>
