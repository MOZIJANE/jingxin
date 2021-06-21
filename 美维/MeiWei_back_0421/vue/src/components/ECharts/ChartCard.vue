<template>
  <el-card>
    <div class="chart-wrapper" ref="chartWrapper">
      <e-charts v-if="hasData"
        :w="frame.width"
        :h="frame.height"
        :options="options"
        :init-options="{renderer: 'canvas'}"
        auto-resize
      ></e-charts>
      <div v-else
        :style="{width: frame.width + 'px', height: frame.height +'px'}"
      >
        <el-button type="warning" plain disabled>没有数据</el-button>
      </div>
    </div>
  </el-card>
</template>

<script>
import Echarts from '@/components/ECharts';

export default {
  name: 'chart-card',
  components: {
    'e-charts': Echarts,
  },
  props: {
    options: {
      type: Object,
      default() {
        return { series: [] };
      },
    },
  },
  data() {
    return {
      frame: {
        width: 600,
        height: 400,
      },
    };
  },
  computed: {
    hasData() {
      const { dataset, series } = this.options;
      if (dataset && dataset.source.length > 0) {
        return true;
      }
      if (series && series.length > 0) {
        return true;
      }
      return false;
    },
  },
  methods: {
    setFrame() {
      const { $el } = this;
      if ($el) {
        const width = $el.clientWidth - 40;
        const height = $el.clientHeight - 98;
        this.frame = { width, height };
      }
    },
  },
  mounted() {
    this.setFrame();
  },
};
</script>
