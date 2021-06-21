<template>
  <div>
    <el-card style="height:60vh; width: 100%;" :body-style="{ position: 'relative' }">
      <el-tabs type="border-card">
        <el-tab-pane>
          <span slot="label">{{title}}</span>
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
              <el-tooltip class="item" effect="dark" :content="locationTip" placement="left-start">
                <el-button :plain=true style="border-color:#cccccc;font-weight:bold;width: 20px" :class="{'color-show':isLocation,'color-hide':!isLocation}" :onmouseover="locationColor" :onMouseOut="locationColor" @click="handleLocation">
                  <icon name="map-marker-alt" style="margin-left: -6px;"></icon>
                </el-button>
              </el-tooltip>
            </el-button-group>
          </div>
          <div id="svg-wrapper">
            <svg id="svg1" v-if="type === 'CAD'" :viewBox="viewBox" xmlns="http://www.w3.org/2000/svg" ref="map" @mousedown="dragMap" @mouseup="dragMapUp1" :class="{'point-move':!isLocation,'point-crosshair':isLocation}">
              <cad-map :offsetX="minX" :offsetY="minY" ></cad-map>
            </svg>
            <svg id="svg2" v-else :viewBox="viewBox" xmlns="http://www.w3.org/2000/svg" ref="map" @mousedown="dragMap" @mouseup="dragMapUp2" :class="{'point-move':!isLocation,'point-crosshair':isLocation}">
              <defs>
                <symbol id="agvSymbol" viewBox="0 0 1 1">
                  <path fill="#E86C60" d="M17,0c-1.9,0-3.7,0.8-5,2.1C10.7,0.8,8.9,0,7,0C3.1,0,0,3.1,0,7c0,6.4,10.9,15.4,11.4,15.8 c0.2,0.2,0.4,0.2,0.6,0.2s0.4-0.1,0.6-0.2C13.1,22.4,24,13.4,24,7C24,3.1,20.9,0,17,0z"></path>
               </symbol>
                <marker id="arrowhead" viewBox="0 0 10 10" orient="auto" markerWidth="4" markerHeight="4" refX="10" refY="5">
                  <polygon class="arrowhead" points="0,0 10,5 0,10 3,5" />
                </marker>
              </defs>
              <g v-for="(value, i) in Array(Math.floor(width))" :key="minX+i" class="svg-grid">
                <line
                  :x1="minX + i * 1"
                  :y1="minY"
                  :x2="minX + i * 1"
                  :y2="maxY"
                  stroke="#859eff"
                  stroke-width="0.003"
                ></line>
              </g>
              <g v-for="(value, i) in Array(Math.floor(height))" :key="minY+i" class="svg-grid">
                <line
                  :x1="minX"
                  :y1="minY + i * 1"
                  :x2="maxX"
                  :y2="minY + i * 1"
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
                    :key="advancedCurve.startPoint+'->'+advancedCurve.endPoint"
                    :d="resolveBezierPath(advancedCurve)"
                    @click="selectAdvancedCurve(i)"
                    marker-end="url(#arrowhead)"
                  ></path>
                </template>
              </g>
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
            </svg>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import 'vue-awesome/icons/unlink';
import CadMap from '@/components/CADMap/8-222';
import { getFloors, getMapStatic, getAgvStatusList, agvGoHome, agvUnlock } from '@/services';

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
  name: 'cotent-Map',
  components: {
    CadMap,
  },
  props: {
    title: String,
    type: String,
  },
  filters: {
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
      isLocation: false,
      center: { x: 0, y: 0 },
      viewBox: '0 0 0 0',
      header: { minPos: {}, maxPos: {} },
      normalPointList: [],
      advancedPointList: [],
      advancedCurveList: [],
      activeCurve: '',
      agvStatusList: {},
      agvTable: [],
    };
  },
  computed: {
    locationColor() {
      return `this.style.color='${this.isLocation ? 'dodgerblue' : '#606266'}'`;
    },
    locationTip() {
      return this.isLocation ? '取消定位' : '位置定位';
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
    advancedPositions() {
      const obj = {};
      this.advancedPointList.forEach(({ name, x, y }) => {
        obj[name] = {};
        obj[name].x = x;
        obj[name].y = y;
      });
      return obj;
    },
  },
  methods: {
    handleAdjust() {
      const { header } = this;
      this.zoom = 1;
      this.center = {
        x: (header.minPos.x + header.maxPos.x) / 2,
        y: (header.minPos.y + header.maxPos.y) / 2,
      };
      this.viewBox = `${header.minPos.x} ${header.minPos.y} ${(header.maxPos.x - header.minPos.x)} ${(header.maxPos.y - header.minPos.y)}`;
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
      const { zoom, header, width, height } = this;
      this.zoom = zoom * 1.1;
      this.viewBox = `${header.minPos.x} ${header.minPos.x} ${width / this.zoom} ${height / this.zoom}`;
    },
    handleZoomOut() {
      const { header, zoom, width, height } = this;
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
      this.viewBox = `${header.minPos.x} ${header.minPos.y} ${width / this.zoom} ${height / this.zoom}`;
    },
    triggerGoHome(agvId) {
      agvGoHome(agvId)
        .then(() => (this.$message.success(`${agvId} 返回原点请求成功!`)))
        .catch(() => (this.$message.error(`${agvId} 返回原点请求失败!`)));
    },
    handleLocation() {
      this.isLocation = !this.isLocation;
    },
    triggerUnlock(agvId) {
      agvUnlock(agvId)
        .then(() => (this.$message.success(`${agvId} 解锁请求成功!`)))
        .catch(() => (this.$message.error(`${agvId} 解锁请求失败!`)));
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
    fetchAgvStatusList() {
      this.agvStatusList = {};
      this.agvTable = [];
      getAgvStatusList(this.floorId).then(({ list }) => {
        this.agvStatusList = list;
        this.agvTable = objToList(list);
      });
    },
    isChargePoint(className) {
      return className === 'ChargePoint';
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
      if (this.isLocation) {
        return;
      }
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
    dragMapUp1(e) {
      const svg = document.getElementById('svg1');
      const ctm = svg.getScreenCTM();
      const pt = svg.createSVGPoint();
      pt.x = e.clientX;
      pt.y = e.clientY;
      const mf = pt.matrixTransform(ctm.inverse());
      const p = {
        x: mf.x.toFixed(3),
        y: mf.y.toFixed(3),
      };
      if (this.isLocation) {
        this.$emit('listenToChildEvent', p);
      }
    },
    dragMapUp2(e) {
      const svg = document.getElementById('svg2');
      const ctm = svg.getScreenCTM();
      const pt = svg.createSVGPoint();
      pt.x = e.clientX;
      pt.y = e.clientY;
      const mf = pt.matrixTransform(ctm.inverse());
      const p = {
        x: mf.x.toFixed(3),
        y: mf.y.toFixed(3),
      };
      if (this.isLocation) {
        this.$emit('listenToChildEvent', p);
      }
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
      this.fetchAgvStatusList();
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
      this.fetchAgvStatusList();
    }
  },
};
</script>

<style lang="scss" scoped>
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
.point-move {
  cursor: move;
}
.point-crosshair {
  cursor: crosshair;
}
</style>
