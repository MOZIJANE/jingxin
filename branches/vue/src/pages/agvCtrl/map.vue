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
      <div>
        <el-button-group style="position: absolute;box-shadow: darkgrey 2px 2px 5px 0px;right: 20px;display:flex;flex-direction: column;">
          <el-tooltip class="item" effect="dark" content="自适应" placement="left-start">
            <el-button :plain=true style="border-color:#cccccc;color:dodgerblue;font-weight:bold;width: 20px" @click="handleAdjust">
              <icon name="home" style="margin-left: -6px;"></icon>
            </el-button>
          </el-tooltip>
          <el-tooltip class="item" effect="dark" content="居中" placement="left-start">
            <el-button :plain=true style="border-color:#cccccc;color:dodgerblue;font-weight:bold;width: 20px" @click="handleGoCenter">
              <icon name="arrows-alt" style="margin-left: -6px;"></icon>
            </el-button>
          </el-tooltip>
          <el-tooltip class="item" effect="dark" content="地图调整" placement="left-start" v-if="hasCAD">
            <el-button :plain=true style="border-color:#cccccc;color:dodgerblue;font-weight:bold;width: 20px" @click="handleMapAdjust">
              <icon name="map-marker-alt" style="margin-left: -5px;"></icon>
            </el-button>
          </el-tooltip>
          <el-tooltip class="item" effect="dark" content="缩小一级" placement="left-start">
            <el-button :plain=true style="border-color:#cccccc;color:dodgerblue;font-weight:bold;width: 20px" @click="handleZoomOut">
              <icon name="search-minus" style="margin-left: -6px;"></icon>
            </el-button>
          </el-tooltip>
          <el-tooltip class="item" effect="dark" content="放大一级" placement="left-start">
            <el-button :plain=true style="border-color:#cccccc;color:dodgerblue;font-weight:bold;width: 20px" @click="handleZoomIn">
              <icon name="search-plus" style="margin-left: -6px;"></icon>
            </el-button>
          </el-tooltip>
          <el-tooltip class="item" effect="dark" :content="gridTip" placement="left-start">
            <el-button :plain=true style="border-color:#cccccc;font-weight:bold;width: 20px" :class="{'color-show':isGridShow,'color-hide':!isGridShow}" :onmouseover="gridColor" :onMouseOut="gridColor" @click="handleGrid">
              <icon name="th" style="margin-left: -6px;"></icon>
            </el-button>
          </el-tooltip>
          <el-tooltip class="item" effect="dark" :content="spotTip" placement="left-start">
            <el-button plain style="border-color:#cccccc;font-weight:bold;width: 20px" :class="{'color-show':isSpotShow,'color-hide':!isSpotShow}" :onmouseover="spotColor" :onMouseOut="spotColor" @click="handleSpot">
              <icon name="circle" style="margin-left: -6px;"></icon>
            </el-button>
          </el-tooltip>
        </el-button-group>
      </div>
      <div id="svg-wrapper">
        <svg id="svg" :viewBox="viewBox" xmlns="http://www.w3.org/2000/svg" ref="map" @mouseover="setCenter" @mousewheel="zoomMap" @mousedown="dragMap">
          <cad-map :offsetX="minX" :offsetY="minY" v-if="hasCAD"></cad-map>
          <defs>
            <symbol id="agvSymbol" viewBox="0 0 1 1">
              <path fill="#E86C60" d="M17,0c-1.9,0-3.7,0.8-5,2.1C10.7,0.8,8.9,0,7,0C3.1,0,0,3.1,0,7c0,6.4,10.9,15.4,11.4,15.8 c0.2,0.2,0.4,0.2,0.6,0.2s0.4-0.1,0.6-0.2C13.1,22.4,24,13.4,24,7C24,3.1,20.9,0,17,0z"></path>
           </symbol>
            <marker id="arrowhead" viewBox="0 0 10 10" orient="auto" markerWidth="4" markerHeight="4" refX="10" refY="5">
              <polygon class="arrowhead" points="0,0 10,5 0,10 3,5" />
            </marker>
          </defs>
          <g v-for="(value, i) in Array(50)" :key="i" class="svg-grid" v-if="isGridShow">
            <line
              :x1="minX + i * getUnit"
              :y1="minY"
              :x2="minX + i * getUnit"
              :y2="maxY"
              stroke="#859eff"
              stroke-width="0.003"
            ></line>
          </g>
          <g v-for="(value, i) in Array(50)" :key="50+i" class="svg-grid" v-if="isGridShow">
            <line
              :x1="minX"
              :y1="minY + i * getUnit"
              :x2="maxX"
              :y2="minY + i * getUnit"
              stroke="#859eff"
              stroke-width="0.003"
            ></line>
          </g>
          <g id="normal-points" v-if="isSpotShow" :transform="adjust">
            <circle
              v-for="({x,y}, i) in normalPointList"
              class="normal-point"
              :key="'normal-point-'+i"
              :cx="x"
              :cy="y | negate"
              r="0.01"
            ></circle>
          </g>
          <g id="advanced-curves" :transform="adjust">
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
          <g id="advanced-points" :transform="adjust">
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
          <g id="agv-moving" v-if="hasAgv" :transform="adjust">
            <g
              v-for="{ agvId, level, color, x, y, angle=0 } in agvTable"
              v-if="validateAgvLocation(x, y)"
              :key="agvId"
              :transform="'rotate('+radToDeg(-angle)+','+x+','+negateIt(y)+')'"
              fill="#e36116"
              @click="selectAgv(agvId)"
            >
              <rect
                :x="x-0.4"
                :y="(y+0.3) | negate"
                width="0.8"
                height="0.6"
                style="stroke-width: 0.02;stroke: green;fill:#ffffff"
                v-if="agvId === selection"
              ></rect>
              <rect
                :x="x-0.4"
                :y="(y+0.3) | negate"
                rx="0.2"
                ry="0.2"
                width="0.8"
                height="0.6"
                style="stroke-width: 0.03;stroke:#2f2f4f"
              ></rect>
              <polygon
                :points="triangle(x, y)"
                style="stroke:#2f2f4f;stroke-width:0.03;"
              />
            </g>
            <g
              v-for="{ agvId, level, color, x, y} in agvTable"
              v-if="validateAgvLocation(x, y)"
              :key="`text${agvId}`"
              v-tooltip="{ content: '电量：' + parseInt(level*100) + '%',offset: 30}"
            >
              <text
                :x="x-0.22"
                :y="y-0.05 | negate"
                font-size="0.15"
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
          <el-tabs type="border-card">
            <el-tab-pane>
              <span slot="label">AGV 列表</span>
              <el-table :data="agvTable" size="mini">
                <template v-for="{ prop, label } in columns">
                  <el-table-column v-if="prop==='agvId'" :key="prop" :label="label" align="center" width="80">
                    <template slot-scope="scope">
                      <router-link
                        :to="{
                            path: '../agv/status',
                            query: {
                              agvId: scope.row.agvId
                           }
                      }">
                      <span>{{ scope.row.agvId }}</span>
                      </router-link>
                      <i v-if="!scope.row.isActive" class="el-icon-error"></i>
                    </template>
                  </el-table-column>
                  <el-table-column v-else-if="prop==='level'" :key="prop" :label="label" width="100" align="center">
                    <template slot-scope="scope">
                      <!--<el-progress type="circle" color="#67c23a" :width="30" :percentage="Math.floor(scope.row.level*100)" :stroke-width="3"></el-progress>-->
                      <!--<div v-if="scope.row.isCharge">充电中</div>-->
                      <div  :class="{'battery-more' : scope.row.level,'battery-empty' : !scope.row.level}">
                        <div>
                          <el-tooltip class="item" effect="dark" :content="`电量：${String(Math.floor(scope.row.level*100))}%`" placement="top-start">
                            <icon :name=batteryIcon(scope.row.level*100) style="transform: scale(1.5,1.5)"></icon>
                          </el-tooltip>
                        </div>
                        <div v-if="scope.row.isCharge"><icon name="bolt" style="transform: scale(0.6,0.8);margin-left: 3px;margin-top: 2px"></icon></div>
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column v-else-if="prop==='status'" :key="prop" :label="label" width="100" align="center">
                    <template slot-scope="scope">
                      <el-tooltip v-if="scope.row.blocked" class="item" effect="dark" content="阻塞" placement="top-start">
                        <icon name="ban" style="color: #ff4d51;padding-right: 2px"></icon>
                      </el-tooltip>
                      <el-tooltip v-else-if="scope.row.emergency" class="item" effect="dark" content="急停" placement="top-start">
                        <icon name="hand-paper" style="color: #ff4d51"></icon>
                      </el-tooltip>
                      <span v-else>{{getTaskStatus(scope.row.taskStatus)}}</span>
                    </template>
                  </el-table-column>
                  <el-table-column v-else-if="prop==='confidence'" :key="prop" :label="label" width="100" align="center">
                    <template slot-scope="scope">
                      <span>{{scope.row.confidence*100}}%</span>
                    </template>
                  </el-table-column>
                  <el-table-column v-else-if="prop==='target'" :key="prop" :label="label" width="100" align="center">
                    <template slot-scope="scope">
                      <span v-if="scope.row.target">{{scope.row.target}}</span>
                      <span v-else>--</span>
                    </template>
                  </el-table-column>
                  <el-table-column v-else-if="prop==='source'" :key="prop" :label="label" width="100" align="center">
                    <template slot-scope="scope">
                      <span v-if="scope.row.finishedPath">{{scope.row.finishedPath[scope.row.finishedPath.length-1]}}</span>
                      <span v-else>--</span>
                    </template>
                  </el-table-column>
                  <el-table-column v-else-if="prop!='basket'" :key="prop" :prop="prop" :label="label" align="center" width="100"></el-table-column>
                </template>
              </el-table>
            </el-tab-pane>
           </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import 'vue-awesome/icons/unlink';
import CadMap from '@/components/CADMap/8-222';
import { guid } from '@/utils/utils';
import { getFloors, getMapStatic, getMapHistory, wmqtt, getTaskList, getBasketList, getAgvStatusList, agvGoHome, agvUnlock, resetBasket, getCADInfo } from '@/services';

const taskColumns = [
  { prop: '_id', label: '任务编号' },
  { prop: 'taskType', label: '任务类型', width: 120 },
  { prop: 'eId', label: '任务eid' },
  { prop: 'createTime', label: '创建时间', width: 160 },
  { prop: 'status', label: '任务状态' },
];
const columns = [
  { prop: 'agvId', label: '编号' },
  { prop: 'status', label: '状态' },
  { prop: 'level', label: '电量' },
  { prop: 'confidence', label: '置信度' },
  { prop: 'target', label: '目标点' },
  { prop: 'source', label: '当前点' },
  { prop: 'basket', label: '料筐' },
];
const colors = [
  '#F44336', '#2196F3', '#9C27B0', '#FF9800', '#3F51B5',
  '#E91E63', '#03A9F4', '#00BCD4', '#009688', '#4CAF50',
  '#8BC34A', '#CDDC39', '#FFEB3B', '#FFC107', '#673AB7',
  '#FF5722', '#795548', '#9E9E9E', '#607D8B', '#000000',
];
const status = ['正常', '等待', '运行中', '中断', '完成', '失败', '取消'];

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
      blocked,
      emergency,
      confidence,
      target_id: target,
      task_status: taskStatus,
      finished_path: finishedPath,
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
      blocked,
      emergency,
      confidence,
      target,
      taskStatus,
      finishedPath,
    };
  });
}

export default {
  layout: 'platform',
  name: 'cotent-map',
  components: {
    CadMap,
  },
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
        case 2:
          return '待执行';
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
      selection: '',
      isGridShow: true,
      isSpotShow: true,
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
      CADInfo: {},
      hasCAD: false,
    };
  },
  computed: {
    getUnit() {
      return this.hasCAD ? this.CADInfo.scale : 1;
    },
    gridColor() {
      return `this.style.color='${this.isGridShow ? 'dodgerblue' : '#606266'}'`;
    },
    spotColor() {
      return `this.style.color='${this.isSpotShow ? 'dodgerblue' : '#606266'}'`;
    },
    gridTip() {
      return this.isGridShow ? '隐藏网格' : '显示网格';
    },
    spotTip() {
      return this.isSpotShow ? '隐藏点云' : '显示点云';
    },
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
    adjust() {
      if (!this.hasCAD) {
        return '';
      }
      const info = this.CADInfo;
      const offsetX = -info.offsetX;
      const offsetY = -info.offsetY;
      const xx = (-info.rotateX + info.offsetX) * (info.scale - 1);
      const yy = (-info.rotateY + info.offsetY) * (info.scale - 1);
      const rotateX = info.rotateX - info.offsetX;
      const rotateY = info.rotateY - info.offsetY;
      return `rotate(${info.theta},${rotateX},${rotateY}) translate(${xx},${yy}) scale(${info.scale}) translate(${offsetX},${offsetY})`;
    },
  },
  methods: {
    selectAgv(id) {
      this.selection = id;
    },
    triangle(x, y) {
      const path = `${x + 0.27},${-y} ${x + 0.27},${-(y - 0.08)} ${x + 0.35},${-y} ${x + 0.27},${-(y + 0.08)}`;
      return path;
    },
    getTaskStatus(id) {
      const num = parseInt(id, 10);
      return status[num];
    },
    batteryIcon(level) {
      let icon = 'battery-empty';
      if (level === 0) {
        icon = 'battery-empty';
      } else if (level < 25) {
        icon = 'battery-quarter';
      } else if (level < 50) {
        icon = 'battery-half';
      } else if (level < 75) {
        icon = 'battery-three-quarters';
      } else {
        icon = 'battery-full';
      }
      return icon;
    },
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
    handleAdjust() {
      const { header } = this;
      this.zoom = 1;
      this.center = {
        x: (header.minPos.x + header.maxPos.x) / 2,
        y: (header.minPos.y + header.maxPos.y) / 2,
      };
      this.viewBox = `${header.minPos.x} ${header.minPos.y} ${(header.maxPos.x - header.minPos.x)} ${(header.maxPos.y - header.minPos.y)}`;
    },
    handleMapAdjust() {
      this.$router.push({ path: './location', query: { floor: this.floorId } });
    },
    handleTaskList() {
      this.$router.push({ path: '../taskDispatch/taskList', query: { floor: this.floorId } });
    },
    handleGoCenter() {
      const { header } = this;
      this.center = {
        x: (header.minPos.x + header.maxPos.x) / 2,
        y: (header.minPos.y + header.maxPos.y) / 2,
      };
      this.viewBox = `${header.minPos.x / this.zoom} ${header.minPos.y / this.zoom} ${(header.maxPos.x - header.minPos.x) / this.zoom} ${(header.maxPos.y - header.minPos.y) / this.zoom}`;
    },
    handleZoomIn() {
      const { zoom, center, width, height } = this;
      this.zoom = zoom * 1.1;
      this.viewBox = `${center.x - width / this.zoom / 2} ${center.y - height / this.zoom / 2} ${width / this.zoom} ${height / this.zoom}`;
    },
    handleZoomOut() {
      const { header, zoom, center, width, height } = this;
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
      this.viewBox = `${center.x - width / this.zoom / 2} ${center.y - height / this.zoom / 2} ${width / this.zoom} ${height / this.zoom}`;
    },
    handleGrid() {
      this.isGridShow = !this.isGridShow;
    },
    handleSpot() {
      this.isSpotShow = !this.isSpotShow;
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
    fetchCADInfo() {
      getCADInfo(this.floorId)
        .then(({ result }) => {
          if (result.name) {
            this.CADInfo = {
              name: result.name,
              offsetX: parseFloat(result.offsetX),
              offsetY: parseFloat(result.offsetY),
              rotateX: parseFloat(result.rotateX),
              rotateY: parseFloat(result.rotateY),
              scale: parseFloat(result.scale),
              theta: parseFloat(result.theta),
            };
            this.hasCAD = true;
          } else {
            this.hasCAD = false;
          }
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
        this.selection = '';
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
  },
  watch: {
    floorId() {
      this.fetchCADInfo();
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
      this.fetchCADInfo();
      this.fetchMapStatic();
      this.fetchScadaTaskList();
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
.el-button:hover, .el-button:focus {
  color: dodgerblue;
}
.color-show {
  color: dodgerblue;
}
.color-hide {
  color: #606266;
}
.battery-empty {
  color: #ff4d51;
}
.battery-more {
  color: greenyellow;
}
</style>
