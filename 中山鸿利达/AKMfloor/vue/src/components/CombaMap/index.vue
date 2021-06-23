<template>
  <el-card shadow="never" :body-style="{height: '90%', padding: '20px'}" class="map-card">
    <el-amap-search-box class="map-search-box" :search-option="searchOption" :on-search-result="onSearchResult"></el-amap-search-box>
    <el-amap vid="gateway" :plugin="plugin" :zoom="zoom" :center="position">
      <el-amap-marker vid="gateway-marker" :position="position" :events="marker.events" :draggable="marker.draggable"></el-amap-marker>
    </el-amap>
  </el-card>
</template>

<script>
export default {
  name: 'comba-amap',
  props: {
    position: {
      type: Array,
      default() {
        return [113.324587, 23.106487];
      },
    },
  },
  data() {
    return {
      zoom: 12,
      marker: {
        draggable: true,
        events: {
          dragend: (e) => {
            this.$emit('position-change', [e.lnglat.lng, e.lnglat.lat]);
          },
        },
      },
      searchOption: {
        city: '广州',
        citylimit: false,
      },
      plugin: ['ToolBar', 'Scale'],
    };
  },
  methods: {
    onSearchResult(pois) {
      if (pois.length > 0) {
        this.$emit('position-change', [pois[0].lng, pois[0].lat]);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.map-card {
  position: relative;
  .map-search-box {
    position: absolute;
    top: 24px;
    right: 24px;
  }
}
</style>
