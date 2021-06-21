<template>
  <el-card>
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
    dateRange() {
      return {
        dateRangeType: this.$store.state.dateRangeType,
        dateRangeStart: this.$store.state.dateRangeStart,
        dateRangeEnd: this.$store.state.dateRangeEnd,
      };
    },
    requestOption() {
      const { dateRangeType, dateRangeStart, dateRangeEnd } = this.$store.state;
      const eightHours = 8 * 60 * 60 * 1000;
      const sortDir = this.sort.order === 'ascending' ? 'asc' : 'desc';
      return {
        params: {
          dateRangeType,
          dateRangeStart: new Date(dateRangeStart.getTime() + eightHours),
          dateRangeEnd: new Date(dateRangeEnd.getTime() + eightHours),
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
    dateRange: {
      handler() {
        this.fetchData();
      },
      immediate: true,
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
