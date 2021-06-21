<template>
  <div class="smap-bg">
    <el-card v-if="floorId === ''" style="height:92vh; width: 92vw;" :body-style="{ position: 'relative', height: '92vh', display: 'flex', 'justify-content': 'center', 'align-items': 'center', 'z-index': 1000 }">
      <el-select v-model="floorId" placeholder="请选择楼层">
        <el-option
          v-for="{ id, name } in floors"
          :key="id"
          :label="name"
          :value="id">
        </el-option>
      </el-select>
    </el-card>

    <el-card v-else style="height:92vh; width: 92vw;" :body-style="{ position: 'relative' }">
      <div id="svg-wrapper">
        <svg id="svg" :viewBox="viewBox" xmlns="http://www.w3.org/2000/svg" ref="map" @mouseover="setCenter" @mousewheel="zoomMap" @mousedown="dragMap">
          <defs>
            <marker id="arrowhead" viewBox="0 0 10 10" orient="auto" markerWidth="5" markerHeight="5" refX="3" refY="5">
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
              <!-- <line
                class="advanced-curve"
                :class="{ blocked: isLock(advancedCurve.name) }"
                :key="advancedCurve.name"
                :x1="advancedPositions[advancedCurve.sourcePoint].x"
                :y1="advancedPositions[advancedCurve.sourcePoint].y"
                :x2="advancedPositions[advancedCurve.destinationPoint].x"
                :y2="advancedPositions[advancedCurve.destinationPoint].y"
              ></line>
              <text
                v-if="isLock(advancedCurve.name)"
                class="advanced-curve-blocked-text"
                :key="'blocked'+advancedCurve.name"
                :x="(advancedPositions[advancedCurve.sourcePoint].x + advancedPositions[advancedCurve.destinationPoint].x)/2"
                :y="(advancedPositions[advancedCurve.sourcePoint].y + advancedPositions[advancedCurve.destinationPoint].y)/2"
                font-size="0.15"
                transform="translate(-0.15 0)"
                fill="red"
              >block</text> -->
            </template>
          </g>
          <g id="working-path">
            <g v-for="{ agvId, planRoute } in wmqtt['agv/working']" :key="agvId" :stroke="agvList.find(agv => agv.agvId === agvId).color">
              <polyline class="working-path-done" :points="resolvePolylinePath(planRoute.slice(0, agvLocations[agvId] + 1))"></polyline>
              <polyline class="working-path-todo" :points="resolvePolylinePath(planRoute.slice(agvLocations[agvId] + 1))"></polyline>
            </g>
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
              <!-- <circle
                class="advanced-point"
                :key="'point'+advancedPoint.name"
                :cx="advancedPoint.xPosition"
                :cy="advancedPoint.yPosition"
                r="0.058"
                v-tooltip="{ content: '点位：' + advancedPoint.name }"
              ></circle>
              <text
                class="advanced-point-text"
                :key="'text'+advancedPoint.name"
                :x="advancedPoint.xPosition"
                :y="advancedPoint.yPosition"
                font-size="0.18"
                transform="translate(0.05 -0.1)"
              >{{advancedPoint.name}}</text> -->
            </template>
          </g>
        </svg>
      </div>
      <div class="agv-legend">
        <div v-for="{ agvId, color } in agvList" :key="agvId">
          <div class="agv-legend-item">
            <div :style="{ display: 'inline-block', width: '10px', height: '10px', background: color }"></div>
            {{agvId}}
            <icon v-if="!isOnline(agvId)" name="unlink" scale="0.5"></icon>
          </div>
        </div>
      </div>
    </el-card>
    <!-- <el-card v-if="hasAgv" class="agv-list-container">
      <div v-for="{ agvId, level, isCharge } in wmqtt['agv/battery']" :key="agvId">{{agvId}}-{{level}}-{{isCharge}}</div>
    </el-card> -->
  </div>
</template>

<script>
import 'vue-awesome/icons/unlink';
import { guid, fixedZero } from '@/utils/utils';
import { getFloors, getMapStatic, getMapHistory, getPositionInfo, wmqtt } from '@/services';
// import { header, advancedPointList, advancedCurveList } from '@/map.json';

const colors = [
  '#F44336', '#E91E63', '#9C27B0', '#673AB7', '#3F51B5',
  '#2196F3', '#03A9F4', '#00BCD4', '#009688', '#4CAF50',
  '#8BC34A', '#CDDC39', '#FFEB3B', '#FFC107', '#FF9800',
  '#FF5722', '#795548', '#9E9E9E', '#607D8B', '#000000',
];
const agvList = Array(20).fill(1).map((value, index) => {
  const agvId = `AGV${fixedZero(index + 1)}`;
  return { agvId, color: colors[index] };
});

const initiateViewBox = ({ minPos, maxPos }) => `${minPos.x} ${minPos.y} ${maxPos.x - minPos.x} ${maxPos.y - minPos.y}`;
// const newHeader = {
//   ...header,
//   minPos: {
//     x: header.minPos.x,
//     y: -header.maxPos.y,
//     z: header.minPos.z,
//   },
//   maxPos: {
//     x: header.maxPos.x,
//     y: -header.minPos.y,
//     z: header.maxPos.z,
//   },
// };

export default {
  layout: 'smap',
  name: 'cotent-map',
  data() {
    return {
      floors: [],
      floorId: this.$route.query.floor || '',
      scale: 1,
      zoom: 1,
      center: { x: 0, y: 0 },
      viewBox: '0 0 0 0',
      header: { minPos: {}, maxPos: {} },
      advancedPointList: [],
      advancedCurveList: [],
      // center: {
      //   x: (newHeader.minPos.x + newHeader.maxPos.x) / 2,
      //   y: (newHeader.minPos.y + newHeader.maxPos.y) / 2,
      // },
      // viewBox: initiateViewBox(newHeader),
      // header: newHeader,
      // advancedPointList: advancedPointList.map(point => ({ ...point, y: -point.y })),
      // advancedCurveList: advancedCurveList.map((curve) => {
      //   let { controlPos1, controlPos2 } = curve;
      //   controlPos1 = { ...controlPos1, y: -controlPos1.y };
      //   controlPos2 = { ...controlPos2, y: -controlPos2.y };
      //   return {
      //     ...curve,
      //     controlPos1,
      //     controlPos2,
      //   };
      // }),
      activeCurve: '',
      agvList,
      wmqtt: {
        'agv/battery': [
          // { agvId: 'AGV01', level: 0.8, isCharge: true },
        ],
        'agv/location': [],
        'agv/basket': [
          // { agvId: 'AGV01', basket: Array(12).fill(-1) }, // -1: unknown; 0: nothing; 1: raw; 2: product; 3: empty;
        ],
        'map/block': [
          // { name: 'LM15->LM14', startPoint: 'LM15', endPoint: 'LM14' },
        ],
        'map/working': [],
      },
    };
  },
  computed: {
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
      return this.wmqtt['agv/battery'].length !== 0;
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
  },
  methods: {
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
        .then(({ header, advancedPointList, advancedCurveList }) => {
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
    fetchMapHistory() {
      getMapHistory(this.floorId);
      // TODO:
    },
    isChargePoint(className) {
      return className === 'ChargePoint';
    },
    isOnline(id) {
      return this.wmqtt['agv/battery'].find(({ agvId }) => agvId === id);
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
  },
  watch: {
    floorId() {
      this.fetchMapStatic();
      this.handleWmqtt();
    },
  },
  created() {
    getPositionInfo(this.floorId);
    if (this.floorId === '') {
      getFloors().then(({ list }) => {
        this.floors = list;
      });
    }
  },
  mounted() {
    if (this.floorId !== '') {
      this.fetchMapStatic();
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
  stroke: #a1b3c5;
  // stroke: #009900;
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
  stroke-width: 0.075;
  // stroke: #009900;
  stroke: #a1b3c5;
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
  fill: #a1b3c5;
}
.agv-list-container {
  position: absolute;
  z-index: 99;
  width: 92vw;
  bottom: 3vh;
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
  width: 360px;
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

</style>
