<template>
  <el-card>
    <div slot="header" class="clearfix">
      <span class="title">{{title}}</span>
      <div class="picker-wrapper" style="float: right; padding: 3px 0">
        <div v-if="customize" class="picker-customize">
          <el-date-picker
            :size="size"
            v-model="selectedDateRange"
            :picker-options="pickerOptions"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            :clearable="false"
          >
          </el-date-picker>
          <el-button :size="size" icon="el-icon-arrow-left" @click="handleDefault">默认</el-button>
        </div>
        <div v-else class="block picker-default">
          <el-radio-group v-model="label" :size="size">
            <el-radio-button label="日"></el-radio-button>
            <el-radio-button label="周"></el-radio-button>
            <el-radio-button label="月"></el-radio-button>
            <el-radio-button label="年"></el-radio-button>
          </el-radio-group>
          <el-date-picker
            :size="size"
            :key="ui.type"
            :picker-options="dynamicPickerOptions"
            v-model="selectedDate"
            :format="ui.format"
            :type="ui.type"
            :default-time="['00:00:00']"
            placeholder="选择日期"
            :clearable="false"
          ></el-date-picker>
          <el-button :size="size" icon="el-icon-arrow-right" @click="handleCustomize">自定义</el-button>
        </div>
      </div>
    </div>
    <div class="chart-wrapper" ref="chartWrapper">
      <template v-if="hasData">
        <el-row class="el-row">
          <el-col :span="8" style="display: flex; justify-content: flex-start;">
            <el-button size="mini" type="primary" v-loading="exporting" v-if="isExported" @click="exportExcel(`${url}/export`)">导出Excel</el-button>
          </el-col>
          <el-col :span="8" :offset="8">
            <el-input v-model="search.text" size="mini" :placeholder="searchPlaceholder" clearable>
              <el-button slot="append" icon="el-icon-search" @click="handleSearch"></el-button>
            </el-input>
          </el-col>
        </el-row>
        <el-row class="el-row">
          <el-table
            v-loading="tableLoading"
            @sort-change="handleSortChange"
            border
            stripe
            size="mini"
            :data="tableData"
            style="width: 100%"
            :row-style="{ textAlign: 'left' }"
          >
            <template v-for="col in columns">
              <el-table-column v-if="isLink(col)" :key="col.id" :prop="col.id" :label="col.name" :sortable="col.sortable">
                <template slot-scope="scope">
                  <el-button size="mini" type="text" @click="toDetail({ url: col.styleCtrl.redirect.url, id: { [col.styleCtrl.redirect.id]: scope.row[col.styleCtrl.redirect.id] } })">
                    <span>{{ scope.row[col.id] }}</span>
                  </el-button>
                </template>
              </el-table-column>
              <el-table-column v-if="isPopup(col)" :key="col.id" :prop="col.id" :label="col.name" :sortable="col.sortable">
                <template slot-scope="scope">
                  <el-popover
                    placement="top"
                    width="480"
                    trigger="click"
                  >
                    <div v-for="{ label, value } in popupContent" :key="label">
                      <div><strong>{{label}}:</strong>&nbsp;&nbsp;<span>{{value}}</span></div>
                    </div>
                    <el-button slot="reference" size="mini" type="text" @click="fetchPopupData({ url: col.styleCtrl.popup.url, id: scope.row[col.styleCtrl.popup.id] })">
                      <span>{{ scope.row[col.id] }}</span>
                    </el-button>
                  </el-popover>
                </template>
              </el-table-column>
              <el-table-column v-else :key="col.id" :prop="col.id" :label="col.name" :sortable="col.sortable"></el-table-column>
            </template>
          </el-table>
        </el-row>
        <el-row class="el-row">
          <el-pagination
            background
            @size-change="handlePageSizeChange"
            @current-change="handleCurrentPageChange"
            :current-page="pagination.current"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="pagination.pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="pagination.total">
          </el-pagination>
        </el-row>
      </template>
      <div v-else
        :style="{width: frame.width + 'px', height: frame.height +'px'}"
      >
        <el-button type="warning" plain disabled>没有数据</el-button>
      </div>
    </div>
  </el-card>
</template>

<script>
import request from '@/request';

const now = new Date();
const today = [
  new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0),
  new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59),
];
const oneDay = 1000 * 60 * 60 * 24;

export default {
  name: 'comba-date-picker-table',
  props: {
    url: {
      type: String,
    },
    table: {
      type: String,
    },
  },
  data() {
    return {
      popupContent: '',
      exporting: false,
      isExported: false,
      tableLoading: false,
      title: '',
      size: 'mini',
      label: '日',
      selectedDate: now,
      selectedDateRange: today,
      customize: false,
      pickerOptions: {
        firstDayOfWeek: 1,
        shortcuts: [
          {
            text: '上一天',
            onClick(picker) {
              const start = new Date(
                now.getFullYear(),
                now.getMonth(),
                now.getDate(),
                0,
                0,
                0,
              );
              const end = new Date(
                now.getFullYear(),
                now.getMonth(),
                now.getDate(),
                23,
                59,
                59,
              );
              start.setTime(start.getTime() - oneDay);
              end.setTime(end.getTime() - oneDay);
              picker.$emit('pick', [start, end]);
            },
          },
          {
            text: '最近一周',
            onClick(picker) {
              const start = new Date(
                now.getFullYear(),
                now.getMonth(),
                now.getDate(),
                0,
                0,
                0,
              );
              const end = new Date(
                now.getFullYear(),
                now.getMonth(),
                now.getDate(),
                23,
                59,
                59,
              );
              start.setTime(start.getTime() - oneDay * 7);
              picker.$emit('pick', [start, end]);
            },
          },
          {
            text: '最近一个月',
            onClick(picker) {
              const start = new Date(
                now.getFullYear(),
                now.getMonth(),
                now.getDate(),
                0,
                0,
                0,
              );
              const end = new Date(
                now.getFullYear(),
                now.getMonth(),
                now.getDate(),
                23,
                59,
                59,
              );
              start.setTime(start.getTime() - oneDay * 30);
              picker.$emit('pick', [start, end]);
            },
          },
          {
            text: '最近三个月',
            onClick(picker) {
              const start = new Date(
                now.getFullYear(),
                now.getMonth(),
                now.getDate(),
                0,
                0,
                0,
              );
              const end = new Date(
                now.getFullYear(),
                now.getMonth(),
                now.getDate(),
                23,
                59,
                59,
              );
              start.setTime(start.getTime() - oneDay * 90);
              picker.$emit('pick', [start, end]);
            },
          },
          {
            text: '最近半年',
            onClick(picker) {
              const start = new Date(
                now.getFullYear(),
                now.getMonth(),
                now.getDate(),
                0,
                0,
                0,
              );
              const end = new Date(
                now.getFullYear(),
                now.getMonth(),
                now.getDate(),
                23,
                59,
                59,
              );
              start.setTime(start.getTime() - oneDay * 180);
              picker.$emit('pick', [start, end]);
            },
          },
          {
            text: '最近一年',
            onClick(picker) {
              const start = new Date(
                now.getFullYear(),
                now.getMonth(),
                now.getDate(),
                0,
                0,
                0,
              );
              const end = new Date(
                now.getFullYear(),
                now.getMonth(),
                now.getDate(),
                23,
                59,
                59,
              );
              start.setTime(start.getTime() - oneDay * 365);
              picker.$emit('pick', [start, end]);
            },
          },
        ],
      },
      tableData: [],
      columns: [],
      sort: {
        prop: '',
        order: 'ascending',
      },
      pagination: {
        pageSize: 10,
        current: 1,
        total: 0,
      },
      search: {
        text: '',
      },
    };
  },
  computed: {
    dynamicPickerOptions() {
      const { label } = this;
      let shortcuts;
      if (label === '日') {
        shortcuts = [
          {
            text: '昨天',
            onClick(picker) {
              const yesterday = new Date(Date.now() - oneDay);
              picker.$emit('pick', yesterday);
            },
          },
        ];
      }
      if (label === '周') {
        shortcuts = [
          {
            text: '上一周',
            onClick(picker) {
              const oneWeekAgo = new Date(Date.now() - oneDay * 7);
              picker.$emit('pick', oneWeekAgo);
            },
          },
        ];
      }
      if (label === '月') {
        shortcuts = [
          {
            text: '上一个月度',
            onClick(picker) {
              const oneMonthAgo = new Date(Date.now() - oneDay * 30);
              picker.$emit('pick', oneMonthAgo);
            },
          },
        ];
      }
      if (label === '年') {
        shortcuts = [
          {
            text: '上一个年度',
            onClick(picker) {
              const oneYearAgo = new Date(Date.now() - oneDay * 365);
              picker.$emit('pick', oneYearAgo);
            },
          },
        ];
      }
      return {
        firstDayOfWeek: 1,
        shortcuts,
      };
    },
    searchPlaceholder() {
      const searchableFields = this.columns.filter(field => field.searchable);
      const searchableText = searchableFields.map(field => field.name);
      return `搜索 ${searchableText.toString()}`;
    },
    frame() {
      const { $el } = this;
      if ($el) {
        const width = $el.clientWidth - 40;
        const height = $el.clientHeight - 98;
        return { width, height };
      }
      return { width: 600, height: 400 };
    },
    ui() {
      const { customize, label } = this;
      if (customize) {
        return { type: 'dates', format: 'yyyy 年 M 月 dd 日' };
      }
      let ret;
      switch (label) {
        case '周':
          ret = { type: 'week', format: 'yyyy 第 W 周' };
          break;
        case '月':
          ret = { type: 'month', format: 'yyyy 第 M 月' };
          break;
        case '年':
          ret = { type: 'year', format: 'yyyy 年度' };
          break;
        default:
          ret = { type: 'date', format: 'yyyy 年 M 月 dd 日' };
      }
      return ret;
    },
    period() {
      const { ui: { type }, selectedDate, selectedDateRange, customize } = this;
      if (customize) {
        return selectedDateRange;
      }

      const year = selectedDate.getFullYear();
      const month = selectedDate.getMonth();
      const date = selectedDate.getDate();
      let start;
      let end;
      if (type === 'date') {
        start = new Date(year, month, date, 0, 0, 0);
        const endTime = start.getTime() + oneDay - 1;
        end = new Date(endTime);
      } else if (type === 'week') {
        let day = selectedDate.getDay();
        if (day === 0) {
          day = 6;
        } else {
          day -= 1;
        }
        start = new Date(year, month, date - day, 0, 0, 0);
        end = new Date(start.getTime() + 7 * oneDay - 1);
      } else if (type === 'month') {
        start = new Date(year, month, 1, 0, 0, 0);
        end = new Date(year, month + 1, 1, 0, 0, 0);
        end.setTime(end.getTime() - 1);
      } else {
        start = new Date(year, 0, 1, 0, 0, 0);
        end = new Date(year + 1, 0, 1, 0, 0, 0);
        end.setTime(end.getTime() - 1);
      }
      return [start, end];
    },
    requestOption() {
      const { period, ui: { type } } = this;
      const [start, end] = period;
      const eightHours = 8 * 60 * 60 * 1000;
      const sortDir = this.sort.order === 'ascending' ? 'asc' : 'desc';
      return {
        params: {
          dateRangeType: type,
          dateRangeStart: new Date(start.getTime() + eightHours),
          dateRangeEnd: new Date(end.getTime() + eightHours),
        },
        data: {
          pageSize: this.pagination.pageSize,
          current: this.pagination.current,
          table: this.table,
          sortId: this.sort.prop,
          sortDir,
          searchText: this.search.text,
        },
      };
    },
    hasData() {
      return this.tableData.length !== 0;
    },
  },
  methods: {
    fetchPopupData({ url, id }) {
      request.get(`${url}&id=${id}`).then(({ list }) => {
        this.popupContent = list;
      });
    },
    toDetail(payload) {
      this.$store.commit('UPDATE_BIGTABLE', payload);
      this.$router.push(payload.url);
    },
    isLink(col) {
      if (col.styleCtrl && col.styleCtrl.redirect) {
        return true;
      }
      return false;
    },
    isPopup(col) {
      if (col.styleCtrl && col.styleCtrl.popup) {
        return true;
      }
      return false;
    },
    handleSearch() {
      this.fetchData();
    },
    handleSortChange({ prop, order }) {
      this.sort.prop = prop;
      this.sort.order = order;
      this.fetchData();
    },
    handlePageSizeChange(val) {
      this.pagination.pageSize = val;
      this.fetchData();
    },
    handleCurrentPageChange(val) {
      this.pagination.current = val;
      this.fetchData();
    },
    handleDefault() {
      this.customize = false;
      this.label = '日';
    },
    handleCustomize() {
      this.customize = true;
      this.label = '日';
    },
    fetchData(url = this.url) {
      this.tableLoading = true;
      request({
        method: 'POST',
        url,
        ...this.requestOption,
      }).then((response) => {
        const { meta, data, page, exportExcel } = response;
        this.isExported = exportExcel;
        this.pagination = page;
        this.columns = meta.filter(({ visible }) => visible);
        this.tableData = data;
        this.sort.prop = meta[0].id;
        this.tableLoading = false;
      });
    },
    exportExcel(url) {
      this.exporting = true;
      request({
        method: 'POST',
        url,
        ...this.requestOption,
      }).then(({ path }) => {
        window.open(`http://${location.host}${path}`, '_blank');
      }).finally(() => { this.exporting = false; });
    },
  },
  watch: {
    period: {
      handler() {
        this.fetchData();
      },
      immediate: true,
    },
    table() {
      this.fetchData();
    },
  },
};
</script>

<style lang="scss" scoped>
.clearfix {
  margin-bottom: -0.8rem;
  &:after {
    content: "";
    display: table;
    clear: both;
  }
}
.title {
  display: inline-block;
  line-height: 16px;
  vertical-align: text-bottom;
}
.el-row {
  margin-bottom: 0.5rem;
}
.picker-default,
.picker-customize {
  box-sizing: border-box;
  padding: 0;
  display: flex;
  flex-direction: row;
}
</style>
