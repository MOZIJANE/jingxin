<template>
  <div>
    <el-row :gutter="16">
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12"  :class="{'border-color': position === '1' || position === '3'}">
        <map-model title="图一" v-on:listenToChildEvent="getPointFromChildOne"></map-model>
      </el-col>
      <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12" :class="{'border-color': position === '2' || position === '4'}">
        <map-model type="CAD" title="图二" v-on:listenToChildEvent="getPointFromChildTwo"></map-model>
      </el-col>
    </el-row>
    <el-row :gutter="16">
      <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24">
        <el-card style="margin-top: 16px;width: 100%;">
          <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
          <el-tabs type="border-card">
            <el-tab-pane>
              <span slot="label">定点一</span>
              <div style="">
                <el-radio v-model="position" label="1" border size="medium">图一:（{{point.pointOne.x}},{{point.pointOne.y}}）</el-radio>
                <span> -- </span>
                <el-radio v-model="position" label="2" border size="medium">图二:（{{point.pointTwo.x}},{{point.pointTwo.y}}）</el-radio>
              </div>
            </el-tab-pane>
          </el-tabs>
          </el-col>
          <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
          <el-tabs type="border-card">
            <el-tab-pane>
              <span slot="label">定点二</span>
              <el-radio v-model="position" label="3" border size="medium">图一:（{{point.pointThree.x}},{{point.pointThree.y}}）</el-radio>
              <span> -- </span>
              <el-radio v-model="position" label="4" border size="medium">图二:（{{point.pointFour.x}},{{point.pointFour.y}}）</el-radio>
            </el-tab-pane>
          </el-tabs>
          </el-col>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import 'vue-awesome/icons/unlink';
import mapModel from '@/components/Map/map';
import { saveCADInfo } from '@/services';

export default {
  layout: 'platform',
  name: 'cotent-map',
  components: {
    mapModel,
  },
  data() {
    return {
      position: '1',
      point: {
        pointOne: { x: 0.0, y: 0.0 },
        pointTwo: { x: 0.0, y: 0.0 },
        pointThree: { x: 0.0, y: 0.0 },
        pointFour: { x: 0.0, y: 0.0 },
      },
    };
  },
  computed: {
  },
  methods: {
    getPointFromChildOne(point) {
      console.log(point);
      if (this.position === '1') {
        this.point.pointOne = point;
        this.position = '2';
      } else if (this.position === '3') {
        this.point.pointThree = point;
        this.position = '4';
      }
      this.calculation();
    },
    getPointFromChildTwo(point) {
      console.log(point);
      if (this.position === '2') {
        this.point.pointTwo = point;
        this.position = '3';
      } else if (this.position === '4') {
        this.point.pointFour = point;
        this.position = '1';
      }
      this.calculation();
    },
    calculation() {
      // scale
      let dx = Math.abs(this.point.pointOne.x - this.point.pointThree.x);
      let dy = Math.abs(this.point.pointOne.y - this.point.pointThree.y);
      const dis1 = Math.sqrt((dx ** 2) + (dy ** 2));
      dx = Math.abs(this.point.pointTwo.x - this.point.pointFour.x);
      dy = Math.abs(this.point.pointTwo.y - this.point.pointFour.y);
      const dis2 = Math.sqrt((dx ** 2) + (dy ** 2));
      const scale = (dis2 / dis1).toFixed(3);
      console.log(`scale=${scale}`);
      // offset
      const offsetX = this.point.pointTwo.x - this.point.pointOne.x;
      const offsetY = this.point.pointTwo.y - this.point.pointOne.y;
      console.log(`offset;(${offsetX},${offsetY})`);
      // angle
      const angle1 = Math.atan2((this.point.pointThree.x - this.point.pointOne.x), (this.point.pointThree.y - this.point.pointOne.y));
      const theta1 = angle1 * (180 / Math.PI);
      const angle2 = Math.atan2((this.point.pointFour.x - this.point.pointTwo.x), (this.point.pointFour.y - this.point.pointTwo.y));
      const theta2 = angle2 * (180 / Math.PI);
      const theta = theta2 - theta1;
      console.log(`theta:${theta}`);
      const data = {
        name: this.$route.query.floor,
        scale: (dis2 / dis1),
        offsetX: (this.point.pointOne.x - this.point.pointTwo.x),
        offsetY: (this.point.pointOne.y - this.point.pointTwo.y),
        rotateX: this.point.pointOne.x,
        rotateY: this.point.pointOne.y,
        theta: theta1 - theta2,
      };
      this.handleSaveCADInfo(data);
    },
    handleSaveCADInfo(data) {
      saveCADInfo(data.name, data.scale, data.offsetX, data.offsetY, data.rotateX, data.rotateY, data.theta)
        .then(({ errorno, result }) => {
          console.log(errorno);
          console.log(result);
        });
    },
  },
  watch: {

  },
  created() {
  },
  mounted() {
  },
};
</script>
<style lang="scss" scoped>
.border-color {
  border: 2px solid red
}
</style>
