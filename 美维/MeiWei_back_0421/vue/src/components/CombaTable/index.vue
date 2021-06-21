<template>
  <el-card class="table-card-container">
    <div slot="header" class="clearfix">
      <span class="table-title">{{title}}管理</span>
      <el-button style="float: right; padding: 3px 0" type="text"><i class="el-icon-more"></i></el-button>
    </div>
    <div class="table-wrapper">
      <el-row class="table-banner" type="flex" justify="space-between">
        <el-col :span="8">
          <el-button v-if="permission.create" type="primary" size="mini" @click="popAddDialog" icon="el-icon-circle-plus-outline">新增{{title}}</el-button>
          <el-button v-if="permission.delete" type="danger" size="mini" @click="popMultiDeleteDialog" icon="el-icon-remove-outline">删除{{title}}</el-button>
        </el-col>
        <el-col :span="6">
          <el-input v-model="searchText" v-if="permission.create || permission.edit || permission.delete" size="mini" placeholder="请输入内容" class="input-with-select" :clearable="true">
            <el-button slot="append" icon="el-icon-search"></el-button>
          </el-input>
        </el-col>
      </el-row>

      <el-popover
        placement="right-start"
        width="160"
        v-model="popoverVisible2">
        <p>确定批量删除吗？</p>
        <div style="text-align: right; margin: 0">
          <el-button type="danger" size="mini" @click="popoverVisible2 = false">取消</el-button>
          <el-button type="primary" size="mini" @click="handleMultiDelete">确定</el-button>
        </div>
      </el-popover>
      <el-table :data="chunkData[currentPage-1]" style="width: 100%" size="mini" @selection-change="handleSelectionChange" border :row-style="{ textAlign: 'left' }" v-loading="loading">
        <el-table-column type="selection" width="35"></el-table-column>
        <el-table-column v-for="col in columns" :key="col.id" :col-key="col.id" :prop="col.id" :label="col.name" sortable resizable>
          <template slot-scope="scope">
            <!-- styleCtrl condition -->
            <span v-if="col.styleCtrl && col.styleCtrl.popup">
              <span v-if="Array.isArray(scope.row[col.id])">
                <el-tag v-for="(tag, i) in scope.row[col.id]" :key="i" @click="popupDetailDialog(scope.row, col.id, i)">
                  {{tag}}
                </el-tag>
              </span>
              <span v-else>
                <el-button type="text" size="small" @click="popupDetailDialog(scope.row, col.id, 0)">{{scope.row[col.id]}}</el-button>
              </span>
            </span>
            <!-- end styleCtrl condition -->
            <span v-else-if="col.editCtrl.type === 'select'">
              <span v-if="Array.isArray(scope.row[col.id])">
                <el-tag v-for="(tag, i) in scope.row[col.id]" :key="i">{{tag}}</el-tag>
              </span>
              <span v-else>
                {{scope.row[col.id]}}
              </span>
            </span>
            <span v-else-if="col.editCtrl.type === 'inputPassword'">
              ********
            </span>
            <span v-else>{{scope.row[col.id]}}</span>
          </template>
        </el-table-column>
        <el-table-column v-if="permission.edit || permission.delete" label="操作" fixed="right">
          <template slot-scope="scope">
            <el-button v-if="permission.edit" @click="popEditDialog(scope.row)" type="text" size="small">编辑 </el-button>
            <el-popover
              v-if="permission.delete"
              placement="top"
              width="200"
              trigger="click"
              visible-arrow="true"
              v-model="popoverVisible[scope.$index]"
            >
              <p>确定删除吗</p>
              <div style="text-align: right; margin: 0">
                <el-button type="danger" size="mini" @click="handlePopover(scope.$index)">取消</el-button>
                <el-button type="primary" size="mini" @click="handleDelete(scope.$index,scope.row)">确定</el-button>
              </div>
              <el-button slot="reference" type="text" size="small" @click="handlePopover(scope.$index)"> 删除</el-button>
            </el-popover>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-if="filterTableData.length !== 0"
        class="table-pagination"
        background
        small
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page.sync="currentPage"
        :page-sizes="[5, 10, 20, 50, 100]"
        :page-size="pageSize"
        layout="sizes, total, prev, pager, next"
        :total="total"
      >
      </el-pagination>

      <!-- Form -->
      <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" :fullscreen="fullscreen" :width="dialogStyle.width">
        <!-- <form-item-list :url="url" :columns="columns" :row="currentRow" :onChange="handleInputChange"></form-item-list> -->
        <div class="form-item-list-container">
          <render-function v-if="dialogVisible" :url="url" :columns="columns" :row="currentRow" :form-item-style="formItemStyle" :onChange="handleInputChange" ref="formItermList" :optionsLoaded="optionsLoaded" @load-options="handleLoadOptions"></render-function>
        </div>
        <comba-map
          v-if="hasMap"
          :key="currentRow._id"
          :style="'height: 360px; width: '+mapWidth+'px'"
          :position="[currentRow.longitude, currentRow.latitude]"
          @position-change="handlePositionChange"
        ></comba-map>
        <div slot="footer" class="dialog-footer">
          <el-button type="danger"  @click="closeDialog">取 消</el-button>
          <el-button type="primary" @click="handleSave">确 定</el-button>
        </div>
      </el-dialog>
      <el-dialog title="详细信息" :visible.sync="popoverVisible3">
        <div class="popup-container">
          <el-row v-for="popupDetail in popupDetails" :key="popupDetail.id">
            <el-col :span="8">{{popupDetail.label}}</el-col>
            <el-col :span="16">{{popupDetail.value}}</el-col>
          </el-row>
        </div>
      </el-dialog>
    </div>
  </el-card>
</template>

<script>
import { Message } from 'element-ui';
import qs from 'qs';
import _chunk from 'lodash/chunk';
import axios from '@/request';
import RenderFunction from '@/components/CombaTable/RenderFunction';
import CombaMap from '@/components/CombaMap';

export default {
  name: 'CombaTable',
  components: {
    RenderFunction,
    CombaMap,
  },
  props: {
    url: String,
    table: String,
  },
  data() {
    this.fetchData();
    return {
      loading: false,
      optionsLoaded: {},
      currentPage: 1,
      pageSize: 10,
      dialogVisible: false,
      popoverVisible: [false],
      popoverVisible2: false,
      popoverVisible3: false,
      popupDetails: [],
      dialogTitle: '',
      currentRow: {},
      title: '',
      meta: [],
      formLayout: {},
      tableData: [],
      permission: {},
      multipleSelection: [],
      total: 10,
      formLabelWidth: '120px',
      insert: true,
      searchText: '',
    };
  },
  computed: {
    hasMap() {
      return this.formLayout.type === 'map';
    },
    mapWidth() {
      return Number(this.formLayout.width.replace('px', '')) - 60;
    },
    idField() {
      return this.meta.find(item => item.id === '_id');
    },
    dialogStyle() {
      const { width = '50%' } = this.formLayout;
      return { width };
    },
    formItemStyle() {
      const { split = 0 } = this.formLayout;
      const width = `${100 / (split + 1) - 2}%`;
      return { width, totalWidth: this.formLayout.width };
    },
    fullscreen() {
      return false;
    },
    filterTableData() {
      const { tableData, searchText } = this;
      if (searchText.trim() !== '') {
        return tableData.filter(row =>
          JSON.stringify(row)
            .toUpperCase()
            .includes(searchText.toUpperCase()),
        );
      }
      return tableData;
    },
    ruleForm() {
      const { insert } = this;
      const formData = JSON.parse(JSON.stringify(this.currentRow));
      if (insert) {
        if (this.idField.readonly) {
          delete formData._id;
        }
      }
      return formData;
    },
    columns() {
      return this.meta.filter(col => col.visible);
    },
    defaultRow() {
      const defaults = {};
      this.meta.filter(col => col.id !== '_id').forEach((col) => {
        if (typeof col.editCtrl.default === 'number') {
          defaults[col.id] = col.editCtrl.default;
        } else if (Array.isArray(col.editCtrl.default)) {
          const arr = [];
          col.editCtrl.default.forEach((option) => {
            const int = parseInt(option, 10);
            arr.push(int);
          });
          defaults[col.id] = arr;
        } else if (
          col.editCtrl.type === 'select' &&
            col.editCtrl.attr.multiple === true
        ) {
          defaults[col.id] = col.editCtrl.default || [];
        } else if (col.editCtrl.type === 'inputNumber') {
          defaults[col.id] = col.editCtrl.default || 0;
        } else if (col.editCtrl.type === 'switch') {
          defaults[col.id] = col.editCtrl.default || false;
        } else {
          defaults[col.id] = col.editCtrl.default || '';
        }
      });
      return defaults;
    },
    chunkData() {
      const { filterTableData, pageSize } = this;
      if (filterTableData) {
        return _chunk(filterTableData, pageSize);
      }
      return [];
    },
  },
  methods: {
    handlePositionChange(position) {
      this.currentRow.longitude = position[0];
      this.currentRow.latitude = position[1];
    },
    popupDetailDialog(row, id, index) {
      this.popoverVisible3 = true;
      const api = row['@popup'][id][index];
      axios.get(api).then((res) => {
        this.popupDetails = res.list;
      });
    },
    columnStyleFormatter(col, row) {
      const { styleCtrl = {} } = col;
      const result = {};
      if (styleCtrl.class) {
        result.class = row['@class'][col.id];
      }
      if (styleCtrl.redirect) {
        result.redirect = row['@redirect'][col.id];
      }
      if (styleCtrl.popup) {
        result.popup = row['@popup'][col.id];
      }
      return result; // TODO: custom
    },
    closeDialog() {
      this.dialogVisible = false;
    },
    handleLoadOptions(payload) {
      this.optionsLoaded[payload.id] = payload.list;
    },
    popMultiDeleteDialog() {
      if (this.multipleSelection.length === 0) {
        return Message({
          message: '请至少一列或多列数据',
          type: 'warning',
          showClose: true,
          duration: 800,
        });
      }
      this.popoverVisible2 = true;
      return this;
    },
    handleSelectionChange(val) {
      this.multipleSelection = val;
    },
    handleInputChange(payload) {
      this.currentRow = payload;
    },
    handleSizeChange(val) {
      this.pageSize = val;
    },
    handleCurrentChange(val) {
      this.currentPage = val;
    },
    popAddDialog() {
      this.insert = true;
      this.meta.find(col => col.id === '_id').readonly = false;
      this.currentRow = JSON.parse(JSON.stringify(this.defaultRow));
      this.dialogVisible = true;
      this.dialogTitle = `新增${this.title}`;
    },
    handleSave() {
      this.$refs.formItermList.$children[0].validate((valid) => {
        if (!valid) {
          return Message({
            message: '请填写正确信息',
            type: 'error',
            showClose: true,
            duration: 500,
          });
        }
        const { currentRow, insertOne, updateOne, insert } = this;
        if (insert) {
          if (this.idField.readonly) {
            delete currentRow._id;
          }
          return insertOne(currentRow);
        }
        return updateOne(currentRow);
      });
    },
    handleMultiDelete() {
      if (this.multipleSelection.length !== 0) {
        const idList = [];
        this.multipleSelection.forEach((row) => {
          idList.push(row._id);
        });
        this.deleteData(idList);
        this.popoverVisible2 = false;
      }
    },
    popEditDialog(row) {
      this.insert = false;
      this.currentRow = Object.assign({}, this.defaultRow, row);
      this.meta.find(col => col.id === '_id').readonly = true;
      this.dialogVisible = true;
      this.dialogTitle = `编辑${this.title}`;
    },
    handlePopover(index) {
      if (this.popoverVisible[index]) {
        this.$set(this.popoverVisible, index, false);
      } else {
        this.$set(this.popoverVisible, index, true);
      }
    },
    handleDelete(index, row) {
      this.$set(this.popoverVisible, index, false);
      this.deleteData([row._id]);
    },
    handleFetch(res) {
      const { permission, meta, layout, title, data: tableData } = res;
      this.permission = permission;
      this.meta = meta;
      this.title = title;
      this.tableData = tableData;
      this.total = tableData.length;
      this.formLayout = layout;
    },
    fetchData() {
      this.loading = true;
      const { url, table } = this;
      const method = 'query';
      axios
        .get(url, {
          params: {
            table,
            method,
          },
        })
        .then((res) => {
          this.handleFetch(res);
          this.loading = false;
        });
    },
    deleteData(payload) {
      const { url, table } = this;
      const method = 'delete';
      const api = `${url}?${qs.stringify({ table, method })}`;
      axios
        .post(api, { idList: payload })
        .then(() => {
          this.fetchData();
        });
    },
    insertOne(payload) {
      const { url, table } = this;
      const method = 'insert';
      const api = `${url}?${qs.stringify({ table, method })}`;
      axios
        .post(api, { ...payload })
        .then(() => {
          this.dialogVisible = false;
          this.fetchData();
        });
    },
    updateOne(payload) {
      const { url, table } = this;
      const method = 'update';
      const api = `${url}?${qs.stringify({ table, method })}`;
      axios
        .post(api, { ...payload })
        .then(() => {
          this.dialogVisible = false;
          this.fetchData();
        });
    },
  },
};
</script>

<style lang="scss" scoped>
.table-card-container {
  border-radius: 1px;
  box-shadow: 0 0 6px 0 rgba(0, 0, 0, 0.05);
  border: none;
  .table-wrapper {
    width: 100%;
  }
  .table-title {
    font-size: 1.2rem;
    font-weight: 500;
  }
  .table-banner {
    margin: 0 0 0.5rem;
  }
  .table-pagination {
    margin: 0.5rem 0;
    padding: 2px 0;
  }
}
.form-item-list-container {
  padding-right: 2%;
}
</style>
