<template>
  <div class="smap-bg">
    <el-card class="agv-tray-container">
      <transition name="bounce">
        <div class="agv-tray-next" v-if="sn && taskStatus === 1">
          <h2> SN NO: <em>{{sn}}</em></h2>
          <el-row :gutter="20">
            <el-col v-for="(tray, index) in trays" :key="index" :span="4">
              <div class="agv-tray-box" :class="{'agv-tray-selected': tray}" @mouseover="showOverlay(index)" @mouseout="hideOverlay(index)">
                料筐 {{ index+1 }}
                <br/>
                {{ baskets[index] }}
                <transition v-if="overlays[index]">
                  <div v-if="tray" class="agv-tray-overlay">
                    <el-button round type="info" @click="toggleTray(index)">取消</el-button>
                  </div>
                  <div v-else class="agv-tray-overlay">
                    <el-button round type="success" @click="toggleTray(index)">选择</el-button>
                  </div>
                </transition>
              </div>
            </el-col>
          </el-row>
          <el-checkbox v-model="all" @change="toggleChecked">全选</el-checkbox>
          <el-button type="primary" :loading="uploading" @click="applyTrays" style="float: right; width: 160px;">完成</el-button>
        </div>
        <div class="agv-tray-prev" v-else>
          <div v-if="!isSelected">
            <el-form label-position="top">
              <el-form-item label="选择区域：">
                <el-radio-group v-model="currentArea" @change="handleAreaChange">
                  <el-radio-button v-for="{ label, value } in areas" :key="value" :label="value">{{ label }}</el-radio-button>
                </el-radio-group>
              </el-form-item>
              <el-form-item label="选择位置：">
                <el-cascader
                  expand-trigger="hover"
                  :options="floors"
                  v-model="selectedOptions"
                  placeholder="选择您所在的位置">
                </el-cascader>
              </el-form-item>
            </el-form>
          </div>
          <template v-else>
            <template v-if="isCalling">
              <div class="agv-tray-request__button pulse">等待 AGV</div>
            </template>
            <template v-else>
              <div class="agv-tray-request__button" v-for="{ text, type } in tasks" :key="type" @click="trigerRequest(type)">{{ text }}</div>
            </template>
          </template>
        </div>
      </transition>
    </el-card>
  </div>
</template>

<script>
import { guid } from '@/utils/utils';
import { callAgv, setTrays, getTableData, getFloors, getTaskList, getBasketList } from '@/services';

const isNon = ['空位', '空筐'];
const areas = [
  { label: '原料区', value: 3, table: 'u_raw_position', tasks: [{ text: '下原料', type: 6, from: '空位', to: '原料', none: '空位', full: '原料' }, { text: '上空筐', type: 7, from: '空位', to: '空筐', none: '空位', full: '空筐' }] },
  { label: 'CNC区', value: 1, table: 'u_cnc_position', tasks: [{ text: 'CNC上原料', type: 2, from: '原料', to: '空位', none: '空位', full: '原料' }, { text: 'CNC下空筐', type: 3, from: '空位', to: '空筐', none: '空位', full: '空筐' }] },
  { label: 'BIN区', value: 0, table: 'u_bin_position', tasks: [{ text: 'BIN下成品', type: 1, from: '空位', to: '成品', none: '空位', full: '成品' }, { text: 'BIN上空筐', type: 0, from: '空筐', to: '空位', none: '空位', full: '空筐' }] },
  { label: '成品区', value: 2, table: 'u_product_position', tasks: [{ text: '上成品', type: 4, from: '成品', to: '空位', none: '空位', full: '成品' }, { text: '下空筐', type: 5, from: '空筐', to: '空位', none: '空位', full: '空筐' }] },
];

export default {
  layout: 'smap',
  title: '上料区',
  name: 'cotent-tray',
  data() {
    return {
      baskets: Array(12).fill(null),
      trays: Array(12).fill(false),
      overlays: Array(12).fill(false),
      uploading: false,
      isCalling: false,
      all: false,
      floors: [],
      selectedOptions: [],
      sn: null,
      taskStatus: null,
      areas,
      currentArea: null,
      task: null,
    };
  },
  computed: {
    tasks() {
      const { tasks } = areas.find(area => area.value === this.currentArea);
      return tasks;
    },
    isSelected() {
      return this.selectedOptions.length !== 0;
    },
    activeEid() {
      if (!this.isSelected) {
        return null;
      }
      return this.selectedOptions[1].split('-')[0];
    },
    activePayload() {
      if (!this.isSelected) {
        return null;
      }
      return this.selectedOptions[1].split('-')[1];
    },
  },
  methods: {
    toggleChecked(val) {
      if (val) {
        this.trays.fill(true);
      } else {
        this.trays.fill(false);
      }
    },
    showOverlay(index) {
      this.overlays.splice(index, 1, true);
    },
    hideOverlay(index) {
      this.overlays.splice(index, 1, false);
    },
    hideOverlays() {
      this.overlays.splice(0, 12, false);
    },
    toggleTray(index) {
      this.hideOverlay(index);
      const tmp = !this.trays[index];
      this.trays.splice(index, 1, tmp);
      // eslint-disable-next-line
      const basketInfo = !tmp
        ? this.task.none
        : isNon.includes(this.task.full)
          ? this.task.full
          : this.activePayload;
      this.baskets.splice(index, 1, basketInfo);
    },
    applyTrays() {
      const { sn, trays, task } = this;
      if (!trays.includes(true) && task.type === 6) {
        this.$message.error('料框不可以全部为空！');
        return;
      }
      if (task.type === 4) {
        this.trays.fill(false);
        this.$message('已经清空所有原料！');
      }
      const basket = this.baskets;
      this.uploading = true;
      setTrays({ sn, basket }).then(() => {
        this.all = false;
        this.uploading = false;
        this.sn = null;
        this.task = null;
        this.taskStatus = null;
        this.isCalling = false;
        this.trays.fill(false);
        this.overlays.fill(false);
      });
    },
    trigerRequest(type) {
      this.task = this.tasks.find(task => task.type === type);
      if (this.isSelected) {
        this.isCalling = true;
        this.sn = `sn-${guid()}`;
        callAgv({
          type,
          eid: this.activeEid,
          sn: this.sn,
        }).then(() => this.checkTaskStatus());
      } else {
        this.$message({
          message: '请选择您所在的位置！',
          type: 'error',
        });
      }
    },
    checkTaskStatus() {
      const currentFloorId = this.selectedOptions[0];
      const interval = setInterval(async () => {
        const { list } = await getTaskList(currentFloorId);
        const { status, agvId } = list.find(({ _id }) => _id === this.sn) || {};
        this.taskStatus = status;
        if (status === 1) {
          const { list: agvList } = await getBasketList(currentFloorId);
          const { basket } = agvList.find(agv => agv._id === agvId);
          this.baskets = basket;
          this.trays = basket.map(item => (item === this.task.none ? 0 : 1));
          this.isCalling = false;
          clearInterval(interval);
        }
      }, 3000);
    },
    handleAreaChange(val) {
      const { table } = areas.find(area => area.value === val);
      this.getCascader(table);
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
            // ...item,
            value: `${item.eId}-${item.payload}`,
            label: `${item.eId} [${item.payload}]`,
          }));
        floor.children = [].concat(children);
      });
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

