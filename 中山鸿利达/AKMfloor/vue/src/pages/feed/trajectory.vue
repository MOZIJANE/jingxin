<template>
  <el-card class="table-card-container">
    <div slot="header" class="clearfix">
      <span class="table-title">手动叫料</span>
      <el-button style="float: right; padding: 3px 0" type="text"><i class="el-icon-more"></i></el-button>
    </div>
    <div class="load-bg">
      <div class="div-style" style="margin-top: 10%">
        <div class="font-style" style="padding-bottom: 10px">
          <span >起始位置：</span>
        </div>
        <el-select v-model="startId" placeholder="请选择" style="width: 300px;">
          <el-option
            v-for="item in Options"
            :key="item.id"
            :label="item.id"
            :value="item.id">
          </el-option>
        </el-select>
      </div>
      <div class="div-style" style="margin-top: 30px">
        <div class="font-style" style="padding-bottom:10px">
          <span>结束位置：</span>
        </div>
        <el-select v-model="endId" placeholder="请选择" style="width: 300px;">
          <el-option
            v-for="item in Options"
            :key="item.id"
            :label="item.id"
            :value="item.id">
          </el-option>
        </el-select>
      </div>
      <div class="div-style" style="margin-top: 30px">
        <el-button type="primary" style="width:390px;" @click="commit">确 定</el-button>
      </div>
      <div class="div-style" style="margin-top: 20px;margin-bottom: 150px">
        <a href="#" class="a-style" @click="popDialog('返航')"><icon name="home" class="icon-style"></icon> 返航</a>
        <a href="#" @click="popDialog('解锁')"><icon name="unlock" class="icon-style"></icon> 解锁</a>
      </div>
    </div>
    <!-- Form -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" :fullscreen="fullscreen" :width="dialogStyle">
      <!-- <form-item-list :url="url" :columns="columns" :row="currentRow" :onChange="handleInputChange"></form-item-list> -->
      <div class="div-style">
        <div class="font-style" style="padding-bottom:10px">
          <span>地图：</span>
        </div>
        <el-select v-model="mapId" placeholder="请选择" style="width: 250px;" @change="getAgvList">
          <el-option
            v-for="item in floorList"
            :key="item.id"
            :label="item.id"
            :value="item.id">
          </el-option>
        </el-select>
      </div>
      <div class="div-style" style="margin-top: 20px">
        <div class="font-style" style="padding-bottom:10px">
          <span>Agv：</span>
        </div>
        <el-select v-model="agvId" placeholder="请选择" style="width: 250px;">
          <el-option
            v-for="item in agvList"
            :key="item.id"
            :label="item.id"
            :value="item.id">
          </el-option>
        </el-select>
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button type="danger"  @click="closeDialog">取 消</el-button>
        <el-button type="primary" @click="handleSave">确 定</el-button>
      </div>
    </el-dialog>
  </el-card>
</template>

<script>
import { getSeats, setFeed, agvUnlock, agvGoHome, getFloors, getAgvStatusList } from '@/services';
import ChartCard from '@/components/ECharts/ChartCard';
import ElCol from 'element-ui/packages/col/src/col';

export default {
  layout: 'platform',
  name: 'agv-load',
  components: {
    ElCol,
    ChartCard,
  },
  data() {
    this.fetchData();
    this.getFloorList();
    return {
      dialogVisible: false,
      dialogTitle: '',
      mapId: '',
      agvId: '',
      Options: [],
      floorList: [],
      agvList: [],
      startId: '',
      endId: '',
    };
  },
  computed: {
    dialogStyle() {
      return '400px';
    },
    fullscreen() {
      return false;
    },
  },
  methods: {
    fetchData() {
      getSeats().then(({ info }) => {
        if (info.length !== 0) {
          this.Options = info;
        }
      });
    },
    getFloorList() {
      getFloors().then(({ list }) => {
        if (list.length !== 0) {
          this.floorList = list;
        }
      });
    },
    getAgvList(mapId) {
      this.agvList = [];
      getAgvStatusList(mapId).then(({ list }) => {
        if (list.length !== 0) {
          Object.keys(list).map((key) => {
            this.agvList.push({});
            this.agvList[this.agvList.length - 1].id = key;
            return key;
          });
        }
      });
    },
    closeDialog() {
      this.dialogVisible = false;
    },
    handleSave() {
      if (this.mapId === '') {
        this.$message({
          message: '请选择地图！',
          type: 'error',
        });
        return;
      }
      if (this.agvId === '') {
        this.$message({
          message: '请选择Agv！',
          type: 'error',
        });
        return;
      }
      if (this.dialogTitle === '返航') {
        agvGoHome(this.agvId)
          .then(() => (this.$message.success(`${this.agvId} 返回原点请求成功!`)))
          .catch(() => (this.$message.error(`${this.agvId} 返回原点请求失败!`)));
      } else {
        agvUnlock(this.agvId)
          .then(() => (this.$message.success(`${this.agvId} 解锁请求成功!`)))
          .catch(() => (this.$message.error(`${this.agvId} 解锁请求失败!`)));
      }
      this.dialogVisible = false;
    },
    popDialog(title) {
      this.dialogTitle = title;
      this.agvId = '';
      this.mapId = '';
      this.agvList = [];
      this.dialogVisible = true;
    },
    commit() {
      let startNum;
      let endNum;

      if (this.startId.length === 0) {
        this.$message({
          message: '请选择起始位置！',
          type: 'error',
        });
        return;
      }
      if (this.endId.length === 0) {
        this.$message({
          message: '请选择结束位置！',
          type: 'error',
        });
        return;
      }
      if (this.endId === this.startId) {
        this.$message({
          message: '起始位置与结束位置不能一样！',
          type: 'error',
        });
        return;
      }
      this.Options.map((item, index) => {
        if (item.id === this.startId) {
          startNum = index;
        }
        if (item.id === this.endId) {
          endNum = index;
        }
        return index;
      });
      const seat1 = this.Options[startNum].id;
      const location1 = this.Options[startNum].location;
      const floorId1 = this.Options[startNum].floorId;
      const direction1 = this.Options[startNum].direction;
      const seat2 = this.Options[endNum].id;
      const location2 = this.Options[endNum].location;
      const floorId2 = this.Options[endNum].floorId;
      const direction2 = this.Options[endNum].direction;
      setFeed({ seat1, location1, floorId1, direction1, seat2, location2, floorId2, direction2 })
        .then(() => (this.$message.success('请求成功!')))
        .catch(() => (this.$message.error('请求失败!')));
    },
  },
};
</script>
<style lang="scss" scoped>
  .mb3 {
    margin-bottom: 16px;
  }
  .load-bg {
    border:1px solid #e9eef3;
    margin-top: 10px;
  }
  .div-style {
    display: flex;
    justify-content: center;
    align-items: center;
  }
  .a-style {
    margin-left:270px;
    margin-right: 20px
  }
  .icon-style {
    width: 12px;
    height: 12px;
    padding-top: 1px;
  }
  .font-style {
    font-size: 16px;
    font-weight: 600;
    padding-top: 5px;
    padding-right: 10px;
  }
  a:link {
    font-size: 14px;
    color: #1C86EE;
    text-decoration: none;
  }
  a:visited {
    font-size: 14px;
    color: #1C86EE;
    text-decoration: none;
  }
  a:hover {
    font-size: 14px;
    color: #0000FF;
    cursor: hand;
    text-decoration: underline;
  }
</style>
