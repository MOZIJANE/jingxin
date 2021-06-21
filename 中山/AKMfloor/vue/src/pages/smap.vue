<template>
  <div>
    <el-card v-if="floorId === ''" style="height:80vh; width: 100%;" :body-style="{ position: 'relative', height: '80vh', display: 'flex', 'justify-content': 'center', 'align-items': 'center', 'z-index': 1000 }">
      <el-select v-model="floorId" placeholder="请选择楼层">
        <el-option
          v-for="{ id, name } in floors"
          :key="id"
          :label="name"
          :value="id">
        </el-option>
      </el-select>
    </el-card>

    <el-card v-else style="height:80vh; width: 100%;" :body-style="{ position: 'relative' }">
      <div id="svg-wrapper">
        <svg id="svg" :viewBox="viewBox" xmlns="http://www.w3.org/2000/svg" ref="map" @mouseover="setCenter" @mousewheel="zoomMap" @mousedown="dragMap">
          <defs>
            <symbol id="agvSymbol" viewBox="0 0 1 1">
              <path fill="#E86C60" d="M17,0c-1.9,0-3.7,0.8-5,2.1C10.7,0.8,8.9,0,7,0C3.1,0,0,3.1,0,7c0,6.4,10.9,15.4,11.4,15.8 c0.2,0.2,0.4,0.2,0.6,0.2s0.4-0.1,0.6-0.2C13.1,22.4,24,13.4,24,7C24,3.1,20.9,0,17,0z"></path>
           </symbol>
            <marker id="arrowhead" viewBox="0 0 10 10" orient="auto" markerWidth="4" markerHeight="4" refX="10" refY="5">
              <polygon class="arrowhead" points="0,0 10,5 0,10 3,5" />
            </marker>
          </defs>
          <g v-for="(value, i) in Array(40)" :key="i" class="svg-grid">
            <line
              :x1="minX + i * width / 40"
              :y1="minY"
              :x2="minX + i * width / 40"
              :y2="maxY"
              stroke="#859eff"
              stroke-width="0.003"
            ></line>
            <line
              :x1="minX"
              :y1="minY + i * height / 20"
              :x2="maxX"
              :y2="minY + i * height / 20"
              stroke="#859eff"
              stroke-width="0.003"
            ></line>
          </g>
          <g id="normal-points">
            <circle
              v-for="({x,y}, i) in normalPointList"
              class="normal-point"
              :key="'normal-point-'+i"
              :cx="x"
              :cy="y | negate"
              r="0.01"
            ></circle>
          </g>
          <g id="advanced-curves">
            <template v-for="advancedCurve in advancedCurveList">
              <path
                class="advanced-curve"
                :class="{ blocked: isLock(advancedCurve) }"
                :key="advancedCurve.startPoint+'->'+advancedCurve.endPoint"
                :d="resolveBezierPath(advancedCurve)"
                @click="selectAdvancedCurve(i)"
                marker-end="url(#arrowhead)"
              ></path>
            </template>
          </g>
          <!-- <g id="working-path">
            <g v-for="{ agvId, planRoute } in wmqtt['agv/working']" :key="agvId" :stroke="agvList.find(agv => agv.agvId === agvId).color">
              <polyline class="working-path-done" :points="resolvePolylinePath(planRoute.slice(0, agvLocations[agvId] + 1))"></polyline>
              <polyline class="working-path-todo" :points="resolvePolylinePath(planRoute.slice(agvLocations[agvId] + 1))"></polyline>
            </g>
          </g> -->
          <g id="advanced-points">
            <template v-for="{ name, className, x, y } in advancedPointList">
              <circle
                class="advanced-point"
                :class="{ 'charge-point': isChargePoint(className)}"
                :key="'point'+name"
                :cx="x"
                :cy="y"
                r="0.058"
                v-tooltip="{ content: '点位：' + name }"
              ></circle>
              <text
                class="advanced-point-text"
                :key="'text'+name"
                :x="x"
                :y="y"
                font-size="0.18"
                transform="translate(0.05 -0.1)"
              >{{name}}</text>
            </template>
          </g>
          <g id="agv-moving" v-if="hasAgv">
            <g
              v-for="{ agvId, level, color, x, y, angle=0 } in agvTable"
              v-if="validateAgvLocation(x, y)"
              :key="agvId"
              :transform="'rotate('+radToDeg(-angle)+','+x+','+negateIt(y)+')'"
              :fill="color"
              v-tooltip="{ content: '电量：' + parseInt(level*100) + '%' }"
            >
              <ellipse
                :cx="x"
                :cy="y | negate"
                rx="0.2"
                ry="0.15"
              ></ellipse>
              <rect
                :x="x-0.2"
                :y="(y+0.15) | negate"
                width="0.2"
                height="0.3"
              ></rect>
              <text
                :x="x-0.15"
                :y="y | negate"
                font-size="0.11"
                fill="white"
              >{{agvId}}</text>
            </g>
          </g>
        </svg>
      </div>
    </el-card>
    <el-row :gutter="16">
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card v-if="hasAgv" class="agv-list-container">
          <div slot="header">
            <span>AGV 列表</span>
          </div>
          <el-table :data="agvTable" size="mini">
            <el-table-column key="operation" label="操作" width="50">
              <template slot-scope="scope">
                <icon name="home" scale=".7" class="btn" @click.native="triggerGoHome(scope.row.agvId)"></icon>
                <icon name="unlock-alt" scale=".7" class="btn" @click.native="triggerUnlock(scope.row.agvId)"></icon>
              </template>
            </el-table-column>
            <template v-for="{ prop, label } in columns">
              <el-table-column v-if="prop==='agvId'" :key="prop" :label="label">
                <template slot-scope="scope">
                  <icon name="car" :color="findColorByAgvId(scope.row.agvId)"></icon><span>{{ scope.row.agvId }}</span><i v-if="!scope.row.isActive" class="el-icon-error"></i>
                </template>
              </el-table-column>
              <el-table-column v-else-if="prop==='level'" :key="prop" :label="label" width="50">
                <template slot-scope="scope">
                  <el-progress type="circle" color="#67c23a" :width="30" :percentage="Math.floor(scope.row.level*100)" :stroke-width="3"></el-progress>
                  <div v-if="scope.row.isCharge">充电中</div>
                </template>
              </el-table-column>
              <el-table-column v-else-if="prop==='basket'" :key="prop" :label="label" width="360">
                <template slot-scope="scope">
                  <el-row>
                    <el-col v-for="(item, i) in findBasketByAgvID(scope.row.agvId)" :key="i" :span="4">
                      <el-tag size="mini" :type="setTagColor(item)">{{ item }}</el-tag>
                    </el-col>
                  </el-row>
                </template>
              </el-table-column>
              <el-table-column v-else :key="prop" :prop="prop" :label="label"></el-table-column>
            </template>
          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
        <el-card class="scada-task-list-container" v-if="scadaTaskList.length">
          <div slot="header">
            <span>任务列表</span>
          </div>
          <el-table :data="scadaTaskList" size="mini">
            <template v-for="{ prop, label, width } in taskColumns">
              <el-table-column :key="prop" v-if="prop === 'taskType'" :label="label" :width="width">
                <template slot-scope="scope">
                  <span>{{ scope.row.taskType | taskType }}</span>
                </template>
              </el-table-column>
              <el-table-column :key="prop" v-else-if="prop === 'status'" :label="label">
                <template slot-scope="scope">
                  <span>{{ scope.row.status | taskStatus }}</span>
                </template>
              </el-table-column>
              <el-table-column :key="prop" v-else :prop="prop" :label="label" :width="width"></el-table-column>
            </template>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import 'vue-awesome/icons/unlink';
import { guid } from '@/utils/utils';
import { getFloors, getMapStatic, getMapHistory, wmqtt, getTaskList, getBasketList, getAgvStatusList, agvGoHome, agvUnlock } from '@/services';

const taskColumns = [
  { prop: '_id', label: '任务编号' },
  { prop: 'taskType', label: '任务类型', width: 120 },
  { prop: 'eId', label: '任务eid' },
  { prop: 'createTime', label: '创建时间', width: 160 },
  { prop: 'status', label: '任务状态' },
];
const columns = [
  { prop: 'agvId', label: 'AGV 编号' },
  { prop: 'level', label: '电量' },
  { prop: 'basket', label: '料筐' },
];
const colors = [
  '#F44336', '#2196F3', '#9C27B0', '#FF9800', '#3F51B5',
  '#E91E63', '#03A9F4', '#00BCD4', '#009688', '#4CAF50',
  '#8BC34A', '#CDDC39', '#FFEB3B', '#FFC107', '#673AB7',
  '#FF5722', '#795548', '#9E9E9E', '#607D8B', '#000000',
];

const initiateViewBox = ({ minPos, maxPos }) => `${minPos.x} ${minPos.y} ${maxPos.x - minPos.x} ${maxPos.y - minPos.y}`;

function objToList(agvStatusList) {
  return Object.keys(agvStatusList).map((key) => {
    const agvStatus = agvStatusList[key];
    const agvId = key;
    const level = agvStatus.battery_level;
    const {
      x,
      y,
      angle,
      isActive,
      charging: isCharge,
    } = agvStatus;
    const color = colors[parseInt(key.slice(3), 10) % 20 - 1];
    return {
      agvId,
      level,
      x,
      y,
      angle,
      isCharge,
      color,
      isActive,
    };
  });
}

export default {
  layout: 'platform',
  name: 'cotent-map',
  filters: {
    taskType(value) {
      switch (value) {
        case 0:
          return 'bin区上空筐';
        case 1:
          return 'bin区下成品';
        case 2:
          return 'cnc区上原料';
        case 3:
          return 'cnc区下空筐';
        case 4:
          return '成品区上成品';
        case 5:
          return '品区下空筐';
        case 6:
          return '原料区下原料';
        case 7:
          return '原料区上空筐';
        case 8:
          return 'bin区上下料';
        case 9:
          return 'cnc上下料';
        case 10:
          return 'cnc上备料';
        case 11:
          return '原料区备料';
        default:
          return 'cnc上收筐';
      }
    },
    taskStatus(value) {
      switch (value) {
        case -2:
          return '失败';
        case -1:
          return '等待';
        case 1:
          return '进行中';
        default:
          return '完成';
      }
    },
    negate(value) {
      return -value;
    },
  },
  data() {
    return {
      floors: [],
      scale: 1,
      zoom: 1,
      center: { x: 0, y: 0 },
      viewBox: '0 0 0 0',
      header: { minPos: {}, maxPos: {} },
      normalPointList: [],
      advancedPointList: [],
      advancedCurveList: [],
      activeCurve: '',
      columns,
      wmqtt: {
        'agv/battery': null,
        'agv/location': null,
        'map/block': [
          // { name: 'LM15->LM14', startPoint: 'LM15', endPoint: 'LM14' },
        ],
        'map/working': [],
        'agv/scadaTask': null,
        'agv/basket': null,
        'agv/add': null,
        'agv/status': null,
      },
      taskColumns,
      scadaTaskList: [],
      basketList: [],
      agvStatusList: {},
      agvTable: [],
    };
  },
  computed: {
    floorId() {
      return this.$route.query.floor || '';
    },
    minX() {
      return this.header.minPos.x || 0;
    },
    maxX() {
      return this.header.maxPos.x || 0;
    },
    minY() {
      return this.header.minPos.y || 0;
    },
    maxY() {
      return this.header.maxPos.y || 0;
    },
    width() {
      return this.maxX - this.minX;
    },
    height() {
      return this.maxY - this.minY;
    },
    hasAgv() {
      const { agvStatusList } = this;
      return Object.keys(agvStatusList).length !== 0;
    },
    advancedPositions() {
      const obj = {};
      this.advancedPointList.forEach(({ name, x, y }) => {
        obj[name] = {};
        obj[name].x = x;
        obj[name].y = y;
      });
      return obj;
    },
    agvLocations() {
      const obj = {};
      this.wmqtt['map/working'].forEach(({ agvId, location, planRoute }) => {
        for (let i = 0; i < planRoute.length; i += 1) {
          const { destinationPoint } = planRoute[i];
          if (destinationPoint === location) {
            obj[agvId] = i;
            break;
          }
        }
      });
      return obj;
    },
    latestScadaTask() {
      return this.wmqtt['agv/scadaTask'];
    },
    latestBasketInfo() {
      return this.wmqtt['agv/basket'];
    },
    latestAgvAdd() {
      return this.wmqtt['agv/add'];
    },
    latestAgvStatus() {
      return this.wmqtt['agv/status'];
    },
    latestAgvBattery() {
      return this.wmqtt['agv/battery'];
    },
    latestAgvLocation() {
      return this.wmqtt['agv/location'];
    },
  },
  methods: {
    setTagColor(val) {
      switch (val) {
        case '空位':
          return 'info';
        case '空筐':
          return 'warning';
        default:
          return 'success';
      }
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
    findBasketByAgvID(agvId) {
      const { basket = [] } = this.basketList.find(item => item._id === agvId) || {};
      return basket;
    },
    findColorByAgvId(agvId) {
      const { color = '#aaa' } = this.agvTable.find(item => item.agvId === agvId) || {};
      return color;
    },
    validateAgvLocation(x, y) {
      return typeof x === 'number' && typeof y === 'number';
    },
    radToDeg(value) {
      return value * 180 / Math.PI;
    },
    negateIt(value) {
      return -value;
    },
    handleWmqtt() {
      const topics = Object.keys(this.wmqtt).map(topic => topic.replace('agv/', `agv/${this.floorId}/`));
      wmqtt(this, {
        topics,
        session: `map-${guid()}`,
        maxSize: 20,
        timeSec: 1200,
        frequency: 1000,
      });
    },
    fetchMapStatic() {
      getMapStatic(this.floorId)
        // eslint-disable-next-line
        .then(({ header, advancedPointList, advancedCurveList, points }) => {
          this.normalPointList = points;
          const { minPos, maxPos } = header;
          this.header = {
            ...header,
            minPos: {
              ...minPos,
              y: -maxPos.y,
            },
            maxPos: {
              ...maxPos,
              y: -minPos.y,
            },
          };
          this.advancedPointList = advancedPointList
            .map(point => ({ ...point, y: -point.y }));
          this.advancedCurveList = advancedCurveList
            .map((curve) => {
              let { controlPos1, controlPos2 } = curve;
              controlPos1 = { ...controlPos1, y: -controlPos1.y };
              controlPos2 = { ...controlPos2, y: -controlPos2.y };
              return {
                ...curve,
                controlPos1,
                controlPos2,
              };
            });
          this.viewBox = initiateViewBox(this.header);
          this.center = {
            x: (this.header.minPos.x + this.header.maxPos.x) / 2,
            y: (this.header.minPos.y + this.header.maxPos.y) / 2,
          };
          this.scale = this.resolvePosition().width / this.width;
        });
    },
    fetchScadaTaskList() {
      getTaskList(this.floorId).then(({ list }) => { this.scadaTaskList = list; });
    },
    fetchBasketList() {
      getBasketList(this.floorId).then(({ list }) => { this.basketList = list; });
    },
    fetchAgvStatusList() {
      this.agvStatusList = {};
      this.agvTable = [];
      getAgvStatusList(this.floorId).then(({ list }) => {
        this.agvStatusList = list;
        this.agvTable = objToList(list);
      });
    },
    fetchMapHistory() {
      getMapHistory(this.floorId);
    },
    isChargePoint(className) {
      return className === 'ChargePoint';
    },
    isOnline(id) {
      return this.agvTable.find(({ agvId }) => agvId === id);
    },
    isLock(curve) {
      return this.wmqtt['map/block'].find(({ startPoint, endPoint }) => (startPoint === curve.startPoint && endPoint === curve.endPoint));
    },
    resolvePointPosition(pointName) {
      const { xPosition, yPosition } = this.advancedPoints.find(point => point.name === pointName);
      return {
        x: xPosition,
        y: yPosition,
      };
    },
    resolvePolylinePath(routes) {
      const { advancedPositions } = this;
      const start = advancedPositions[routes[0].sourcePoint];
      const first = `${start.x},${start.y}`;
      const rest = routes
        .map(({ destinationPoint }) => {
          const destination = advancedPositions[destinationPoint];
          return `${destination.x},${destination.y}`;
        })
        .join(' ');
      return `${first} ${rest}`;
    },
    resolveBezierPath(curve) {
      const { advancedPositions } = this;
      const { startPoint, endPoint, controlPos1, controlPos2 } = curve;
      const start = `M ${advancedPositions[startPoint].x},${advancedPositions[startPoint].y}`;
      const end = `${advancedPositions[endPoint].x},${advancedPositions[endPoint].y}`;
      const control = `C ${controlPos1.x},${controlPos1.y} ${controlPos2.x},${controlPos2.y}`;
      const d = `${start} ${control} ${end}`;
      return d;
    },
    selectAdvancedCurve(i) {
      this.activeCurve = i;
    },
    setCenter({ clientX, clientY }) {
      const { zoom, resolvePosition, scale, minX, minY } = this;
      if (zoom === 1) {
        const dx = clientX - resolvePosition().left;
        const dy = clientY - resolvePosition().top;
        const center = {
          x: minX + dx / scale,
          y: minY + dy / scale,
        };
        this.$set(this, 'center', center);
      }
    },
    zoomMap({ deltaY }) {
      // eslint-disable-next-line
      const { header, width, height, center, zoom } = this;
      if (deltaY < 0) {
        this.zoom = zoom * 1.1;
      } else {
        const newZoom = zoom / 1.1;
        if (newZoom < 1) {
          this.zoom = 1;
          this.viewBox = initiateViewBox(header);
          this.center = {
            x: (header.minPos.x + header.maxPos.x) / 2,
            y: (header.minPos.y + header.maxPos.y) / 2,
          };
        } else if (newZoom > 2) {
          this.zoom = 2;
        } else {
          this.zoom = newZoom;
        }
      }
      this.viewBox = `${center.x - width / this.zoom / 2} ${center.y - height / this.zoom / 2} ${width / this.zoom} ${height / this.zoom}`;
    },
    dragMap(e) {
      const { zoom, scale, viewBox } = this;
      const x0 = e.clientX;
      const y0 = e.clientY;
      const [minX, minY, width, height] = viewBox.split(' ');
      document.onmousemove = ({ clientX, clientY }) => {
        const dx = (clientX - x0) / zoom / scale;
        const dy = (clientY - y0) / zoom / scale;
        const newX = parseFloat(minX) - dx;
        const newY = parseFloat(minY) - dy;
        this.viewBox = `${newX} ${newY} ${width} ${height}`;
      };
      document.onmouseup = () => {
        document.onmousemove = null;
        document.onmouseup = null;
      };
    },
    resolvePosition() {
      const svgWrapper = document.getElementById('svg-wrapper');
      const width = svgWrapper.offsetWidth;
      const height = svgWrapper.offsetHeight;
      const left = svgWrapper.offsetLeft + 20 + Math.floor(window.innerWidth * 0.04);
      const top = svgWrapper.offsetTop + 20 + Math.floor(window.innerHeight * 0.04);
      return {
        left,
        top,
        width,
        height,
      };
    },
    handleAgvInfoUpdate(val, list) {
      const { agvId } = val;
      const agvIdList = this[list].map(item => item.agvId);
      if (agvIdList.includes(agvId)) {
        const newList = this[list].map((item) => {
          if (item.agvId === agvId) {
            return { ...item, ...val };
          }
          return item;
        });
        this[list] = newList;
      } else {
        this[list].push(val);
      }
    },
  },
  watch: {
    floorId() {
      this.fetchMapStatic();
      this.fetchScadaTaskList();
      this.fetchBasketList();
      this.fetchAgvStatusList();
      this.handleWmqtt();
    },
    latestScadaTask(val) {
      if ('createTime' in val) {
        if (this.scadaTaskList.length >= 20) {
          this.scadaTaskList.shift();
        }
        this.scadaTaskList.push(val);
      } else {
        this.scadaTaskList.forEach((task) => {
          if (task._id === val._id) {
            // eslint-disable-next-line
            task = { ...task, ...val };
          }
        });
      }
    },
    latestAgvAdd: {
      handler(val) {
        return this.handleAgvInfoUpdate(val, 'basketList');
      },
    },
    latestAgvStatus: {
      handler(val) {
        return this.handleAgvInfoUpdate(val, 'basketList');
      },
    },
    latestAgvBattery: {
      handler(val) {
        return this.handleAgvInfoUpdate(val, 'agvTable');
      },
    },
    latestAgvLocation: {
      handler(val) {
        return this.handleAgvInfoUpdate(val, 'agvTable');
      },
    },
  },
  created() {
    if (this.floorId === '') {
      getFloors().then(({ list }) => {
        this.floors = list;
      });
    }
  },
  mounted() {
    if (this.floorId !== '') {
      this.fetchMapStatic();
      this.fetchScadaTaskList();
      this.fetchBasketList();
      this.fetchAgvStatusList();
      this.handleWmqtt();
    }
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
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
.advanced-point {
  cursor: pointer;
  fill:#fff;
  // stroke: #a1b3c5;
  stroke: #009900;
  stroke-width: 0.024;
  &:hover {
    stroke: rgba(5, 243, 255, 0.538);
  }
  &.charge-point {
    stroke: #26c2d6;
  }
}
.advanced-curve {
  cursor: move;
  fill: none;
  stroke-width: 0.045;
  stroke: #009900;
  // stroke: #a1b3c5;
  &.blocked {
    stroke:rgba(0, 0, 0,.5);
  }
  // &:hover {
  //   stroke:rgba(0, 0, 0,.5);
  // }
}
.advanced-curve-control {
  cursor: pointer;
  fill:greenyellow;
  &:hover {
    fill: red;
    stroke: rgba(255, 34, 0, 0.182);
    stroke-width: 0.2;
  }
}
.arrowhead {
  // fill: #a1b3c5;
  fill: #009900;

}
.agv-list-container,
.scada-task-list-container {
  margin-top: 16px;
  width: 100%;
}
.agv-legend {
  position: absolute;
  top: 20px;
  right: 20px;
  border: 1px solid #dee1e7;
  overflow: hidden;
  font-size: 4px !important;
  color: #303133;
  background: #fff;
  transition: 0.3s;
  padding: 8px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  height: 80px;
  width: 300px;
}
.agv-legend-item {
  display: block;
}
#svg {
  cursor: -webkit-grab;
}

.working-path-todo {
  stroke-dasharray: "20,10,5,5,5,10";
}

.icon-agv {
  width: 14px;
  height: 14px;
  display: inline-block;
}
.btn {
  cursor: pointer;
  &:hover {
    zoom: 1.05;
    color: #26c2d6;
  }
}
</style>
