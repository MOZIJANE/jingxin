<template>
  <div class="system-wrapper">
    <el-tabs type="border-card" v-model="activeTab">
      <el-tab-pane name="first">
        <span slot="label"><i class="el-icon-info"></i> 资源管理</span>

        <el-row>
          <h3 style="float: left;">
            主机
            <el-button plain circle type="primary" icon="el-icon-refresh" size="mini" @click="setHostTable"></el-button>
          </h3>
          <el-table
            v-loading="hostTableLoading"
            :data="hostTableData"
            size="mini"
            style="width: 100%"
            :row-style="{ textAlign: 'left' }"
            border
          >
          <template v-for="col in hostTableColumns">
            <el-table-column
              v-if="col.id === 'disks'"
              :key="col.id"
              :prop="col.id"
              :label="col.name"
              :sortable="col.sortable"
              :width="col.width"
            >
              <template slot-scope="scope">
                <span v-html="scope.row[col.id]"></span>
              </template>
            </el-table-column>
            <el-table-column
              v-else
              :key="col.id"
              :prop="col.id"
              :label="col.name"
              :sortable="col.sortable"
              :width="col.width"
            ></el-table-column>
          </template>
          </el-table>
        </el-row>

        <el-row style="marginTop: 30px;">
         <h3 style="float: left;">
            资源
            <el-radio-group v-model="radio" size="mini" @change="handleRadioChange">
              <el-radio-button label="1分"></el-radio-button>
              <el-radio-button label="5分"></el-radio-button>
              <el-radio-button label="30分"></el-radio-button>
              <el-radio-button label="1小时"></el-radio-button>
              <el-radio-button label="3小时"></el-radio-button>
              <!-- <el-radio-button label="1天"></el-radio-button> -->
            </el-radio-group>
          </h3>
        </el-row>
        <el-row :gutter="8">
          <el-col v-for="chart in charts" :key="chart.ref" :xs="24" :sm="24" :md="24" :lg="12" :xl="12">
            <e-charts
              :key="chart.ref"
              :w="700"
              :h="300"
              :options="chart.options"
              :init-options="{renderer: 'canvas'}"
              auto-resize
            ></e-charts>
          </el-col>
        </el-row>

        <el-row>
          <h3 style="float: left;">
            网络
            <el-button plain circle type="primary" icon="el-icon-refresh" size="mini" @click="setNetTable"></el-button>
          </h3>

          <el-table
            v-loading="netTableLoading"
            :data="netTableData"
            size="mini"
            style="width: 100%"
            :row-style="{ textAlign: 'left' }"
            border
          >
          <template v-for="col in netTableColumns">
            <el-table-column
              :key="col.id"
              :prop="col.id"
              :label="col.name"
              :sortable="col.sortable"
              :width="col.width"
            ></el-table-column>
          </template>
          </el-table>
        </el-row>

      </el-tab-pane>
      <el-tab-pane name="second">
        <span slot="label"><i class="el-icon-sort"></i> 进程管理</span>
        <h3 style="float: left;">
          进程
          <el-button plain circle type="primary" icon="el-icon-refresh" size="mini" @click="setTable"></el-button>
        </h3>
        <el-table
          v-loading="tableLoading"
          :data="tableData"
          size="mini"
          style="width: 100%"
          :row-style="{ textAlign: 'left' }"
        >
        <template v-for="col in tableColumns">
          <el-table-column
            v-if="col.id === 'processes#status'"
            :key="col.id"
            :prop="col.id"
            :label="col.name"
            :sortable="col.sortable"
            :width="col.width"
          >
            <template slot-scope="scope">
              <el-tag
                size="mini"
                :type="calcStatusTagType(scope.row[col.id])"
                disable-transitions>{{scope.row[col.id]}}</el-tag>
            </template>
          </el-table-column>
          <el-table-column
            v-else
            :key="col.id"
            :prop="col.id"
            :label="col.name"
            :sortable="col.sortable"
            :width="col.width"
          ></el-table-column>
        </template>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { getBigTable, getRealTimeChart } from '@/services';
import ECharts from '@/components/ECharts';
import 'echarts';

const option = {
  xAxis: {},
  yAxis: {
  },
  series: [],
};

export default {
  layout: 'platform',
  components: {
    ECharts,
  },
  data() {
    return {
      activeTab: 'first',
      radio: '1分',
      charts: [
        {
          ref: 'cpu',
          url: '/monitor/cpu',
          options: option,
          dateRangeRequestId: '',
          increment: false,
          refresh: 10,
        },
        {
          ref: 'net',
          url: '/monitor/net',
          options: option,
          dateRangeRequestId: '',
          increment: false,
          refresh: 10,
        },
      ],
      options: option,
      tableColumns: [],
      tableData: [],
      tableLoading: false,
      netTableData: [],
      netTableColumns: [],
      netTableLoading: false,
      hostTableData: [],
      hostTableColumns: [],
      hostTableLoading: false,
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
    handleRadioChange() {
      this.charts.forEach((chart) => {
        /* eslint-disable no-param-reassign */
        chart.options.series = [];
        clearInterval(chart.interval);
        /* eslint-disable no-param-reassign */
        chart.dateRangeRequestId = '';
      });
      this.fetchAllData();
    },
    fetchAllData() {
      this.charts.forEach((chart) => {
        getRealTimeChart(chart.url, this.dateRangeLastSec, '').then(({ dateRangeRequestId, refresh, increment, options }) => {
          /* eslint-disable no-param-reassign */
          chart.dateRangeRequestId = dateRangeRequestId;
          chart.refresh = refresh;
          chart.increment = increment;
          chart.options = options;
          chart.interval = setInterval(() => {
            const { url } = chart;
            const { dateRangeLastSec } = this;
            /* eslint-disable no-shadow */
            const dateRangeRequestId = chart.increment ? chart.dateRangeRequestId : '';
            getRealTimeChart(url, dateRangeLastSec, dateRangeRequestId).then((res) => {
              if (res.increment) {
                // const copyXData = [...chart.options.xAxis.data];
                // const newEnd = new Date(res.options.xAxis.data[res.options.xAxis.data.length - 1]);
                // const newEndTimeStamp = newEnd.getTime();
                // const newStartTimeStamp = newEndTimeStamp - this.dateRangeLastSec * 1000;

                const len = res.options.xAxis.data.length;
                for (let j = 0; j < len; j += 1) {
                  /* eslint-disable no-param-reassign */
                  chart.options.xAxis.data.push(res.options.xAxis.data[j]);
                  chart.options.xAxis.data.shift();
                  chart.options.series.forEach((serie, i) => {
                    serie.data.push(res.options.series[i].data[j]);
                    serie.data.shift();
                    // serie.data.push(...res.options.series[i].data)
                  });
                }
                // for (let i=0; i<copyXData.length; i++) {
                //   const datetimestamp = new Date(copyXData[i]).getTime()
                //   if (datetimestamp < newStartTimeStamp) {
                //     chart.options.xAxis.data.shift()
                //     chart.options.series.forEach(serie => serie.data.shift())
                //   } else {
                //     break;
                //   }
                // }
                // chart.options.series.forEach(serie => {
                //   if (serie.data[0] === null) {
                //     let count = 1
                //     for (let i=1; true; i++) {
                //       if (serie.data[i] === null) {
                //         count +=1
                //       } else {
                //         break;
                //       }
                //     }
                //     for (let i=0; i<count; i++) {
                //       serie.data[i] = serie.data[count]
                //     }
                //   }
                // })
              } else {
                /* eslint-disable no-param-reassign */
                chart.options = res.options;
              }
            });
          }, chart.refresh * 1000);
        });
      });
    },
    setTable() {
      this.tableLoading = true;
      getBigTable('r_system').then((res) => {
        this.tableColumns = res.meta;
        this.tableData = res.data;
        this.tableColumns[0].width = '240';
      }).finally(() => {
        // eslint-disable-next-line
        this.tableLoading = false
      });
    },
    setNetTable() {
      this.netTableLoading = true;
      getBigTable('r_system_network').then((res) => {
        this.netTableColumns = res.meta;
        this.netTableData = res.data;
        this.netTableColumns[0].width = '200';
        this.netTableColumns[1].width = '240';
        this.netTableColumns[2].width = '240';
      }).finally(() => {
        // eslint-disable-next-line
        this.netTableLoading = false;
      });
    },
    setHostTable() {
      this.hostTableLoading = true;
      getBigTable('r_system_host').then((res) => {
        this.hostTableColumns = res.meta;
        this.hostTableData = res.data;
        this.hostTableColumns[0].width = '200';
        this.hostTableColumns[1].width = '200';
        this.hostTableColumns[4].width = '400';
      }).finally(() => {
        // eslint-disable-next-line
        this.hostTableLoading = false;
      });
    },
    calcStatusTagType(status) {
      if (status === '异常') {
        return 'danger';
      }
      if (status === '未知') {
        return 'warning';
      }
      return 'success';
    },
  },
  created() {
    this.setTable();
    this.setNetTable();
    this.setHostTable();
  },
  mounted() {
    this.fetchAllData();
  },
  destroyed() {
    this.charts.forEach((chart) => {
      clearInterval(chart.interval);
    });
  },
};
</script>

<style lang="scss" scoped>
  .system-wrapper {
    text-align: left !important;
  }
</style>

