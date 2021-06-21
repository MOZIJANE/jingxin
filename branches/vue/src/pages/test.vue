<template>
  <div class="smap-bg">
    <el-card class="agv-tray-container">
      <el-tabs v-model="activeTab" @tab-click="handleTabChange" tab-position="left" style="height: 500px;">
        <template>
          <el-tab-pane v-for="area in areas" :label="area.label" :key="area.key">
            <h3>{{ area.label }}</h3>
            <el-form :model="ruleForm" :rules="rules" :ref="area.key">
              <el-form-item label="选择设备ID：">
                <el-cascader
                  expand-trigger="hover"
                  :options="floors"
                  v-model="selectedOptions"
                  @change="handleCascaderChange"
                  placeholder="选择您所在的位置">
                </el-cascader>
              </el-form-item>
              <el-form-item label="选择取料点： " v-if="hasEid" v-show="area.key !== 'cncLoad'" prop="gidFrom">
                <el-select v-model="ruleForm.gidFrom" placeholder="取料点">
                  <el-option
                    v-for="gid in gids"
                    :key="gid"
                    :label="gid"
                    :value="gid"
                  ></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="选择下料点： " v-if="hasEid" v-show="['cnc', 'bin'].includes(area.key)" prop="gidTo">
                <el-select v-model="ruleForm.gidTo" placeholder="下料点">
                  <el-option
                    v-for="gid in gids"
                    :key="gid"
                    :label="gid"
                    :value="gid"
                  ></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="选择 AB 位: " v-if="hasEid && !['cncPre', 'bin'].includes(area.key)">
                <el-radio-group v-model="pos">
                  <el-radio label="A">A位</el-radio>
                  <el-radio label="B">B位</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="onSubmit" v-if="hasEid">提交请求</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </template>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import { guid } from '@/utils/utils';
import { getTableData, getFloors, cncFeed, binFeed, cncPreparation, cncLoad, cncUnload } from '@/services';

const areas = [
  { key: 'cnc', label: 'CNC上下料', table: 'u_cnc_position', source: 'u_raw_position' },
  { key: 'bin', label: 'BIN上下料', table: 'u_bin_position', source: 'u_product_position' },
  { key: 'cncPre', label: 'CNC备料', table: 'u_cnc_position', source: 'u_raw_position' },
  { key: 'cncLoad', label: 'CNC上原料', table: 'u_cnc_position', source: 'u_raw_position' },
  { key: 'cncUnload', label: 'CNC上空筐', table: 'u_cnc_position', source: 'u_raw_position' },
];

export default {
  layout: 'smap',
  title: '上下料',
  name: 'cnc-feed',
  data() {
    return {
      activeTab: '0',
      floors: [],
      selectedOptions: [],
      gids: [],
      pos: 'A',
      sn: null,
      areas,
      ruleForm: {
        gidFrom: undefined,
        gidTo: undefined,
      },
      rules: {
        gidFrom: [{ required: true, message: '取料点必选' }],
        gidTo: [{ required: true, message: '下料点必选' }],
      },
    };
  },
  computed: {
    hasEid() {
      return this.selectedOptions.length !== 0;
    },
    activeEid() {
      if (!this.hasEid) {
        return null;
      }
      return this.selectedOptions[1].split('-')[0];
    },
    activePayload() {
      if (!this.hasEid) {
        return null;
      }
      return this.selectedOptions[1].split('-')[1];
    },
  },
  methods: {
    handleTabChange() {
      this.selectedOptions = [];
      this.ruleForm.gidFrom = undefined;
      this.ruleForm.gidTo = undefined;
    },
    handleCascaderChange(val) {
      this.ruleForm.gidFrom = ['3'].includes(this.activeTab) ? 1 : undefined;
      this.ruleForm.gidTo = ['2', '3', '4'].includes(this.activeTab) ? 1 : undefined;
      this.getGidList(val[0]);
    },
    async getCascader(table) {
      const { list } = await getFloors();
      const { data } = await getTableData(table);
      this.floors = list.map(({ id: value, name: label }) => ({
        label,
        value,
        children: [],
      }));
      this.floors.forEach((floor) => {
        const children = data
          .filter(({ floorId }) => floorId === floor.value)
          .map(item => ({
            value: `${item.eId}-${item.payload}`,
            label: `${item.eId} [${item.payload}]`,
          }));
        floor.children = [].concat(children);
      });
    },
    async getGidList(floor) {
      const { data } = await getTableData(this.areas[this.activeTab].source);
      this.gids = data
        .filter(({ floorId }) => floorId === floor)
        .map(item => item.gId);
    },
    onSubmit() {
      const { key } = this.areas[this.activeTab];
      this.$refs[key][0].validate((valid) => {
        if (!valid) {
          this.$message.error('请填写完成信息！');
          return false;
        }
        this.sn = `sn--${guid()}`;
        const payload = {
          sn: this.sn,
          type: this.activePayload,
          eid: this.activeEid,
        };
        let fn;
        switch (key) {
          case 'cnc':
            payload.gid1 = this.ruleForm.gidFrom;
            payload.gid2 = this.ruleForm.gidTo;
            payload.pos = this.pos;
            fn = cncFeed;
            break;
          case 'cncPre':
            payload.gid = this.ruleForm.gidFrom;
            fn = cncPreparation;
            break;
          case 'cncLoad':
            payload.pos = this.pos;
            fn = cncLoad;
            break;
          case 'cncUnload':
            payload.gid = this.ruleForm.gidFrom;
            payload.pos = this.pos;
            fn = cncUnload;
            break;
          default:
            payload.gid1 = this.ruleForm.gidFrom;
            payload.gid2 = this.ruleForm.gidTo;
            fn = binFeed;
            break;
        }
        fn(payload).then(() => {
          this.$message.success('请求成功！');
        });
        return true;
      });
    },
  },
  watch: {
    activeTab: {
      handler(val) {
        const { table } = this.areas[val];
        this.getCascader(table);
      },
      immediate: true,
    },
  },
};
</script>

<style lang="scss" scoped>
.smap-bg {
  background: linear-gradient(-240deg, #574f60, #26c1ab);
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
}
.agv-tray-container {
  width: 80%;
  height: 80%;
  min-width: 900px;
  max-width: 1100px;
  min-height: 660px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
@media screen and (max-width: 1366px){
  .agv-tray-container {
    max-width: 1020px;
    min-height: 600px;
  }
}
.agv-tray-box {
  background: #ccc;
  border-radius: 6px;
  height: 160px;
  margin-bottom: 20px;
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  .agv-tray-overlay {
    position: absolute;
    width: 100%;
    height: 100%;
    z-index: 99;
    background: rgba(0,0,0,.2);
    display: flex;
    justify-content: center;
    align-items: center;
  }
}
.agv-tray-box.agv-tray-selected {
  background: #67c23a;
}
.agv-tray-prev {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  min-height: 600px;
  .agv-tray-request__button {
    margin: 12px;
    width: 200px;
    height: 200px;
    line-height: 200px;
    font-size: 2rem;
    font-weight: 600;
    text-align: center;
    background: #26c1ab;
    box-shadow: 0 0 0 0 rgba(#26c1ab, .5);
    color: #fff;
    border-radius: 50%;
    cursor: pointer;
    &:hover {
      zoom: 1.03;
    }
  }
  .pulse {
    animation: pulse 1.5s infinite;
  }
  @keyframes pulse {
    0% {
      transform: scale(.95);
    }
    70% {
      transform: scale(1);
      box-shadow: 0 0 0 50px rgba(#26c1ab, 0);
    }
    100% {
      transform: scale(.95);
      box-shadow: 0 0 0 0 rgba(#26c1ab, 0);
    }
  }
}
.bounce-enter-active {
  animation: bounce-in .5s;
}
.bounce-leave-active {
  animation: bounce-in .5s reverse;
}
@keyframes bounce-in {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.5);
  }
  100% {
    transform: scale(1);
  }
}
</style>

