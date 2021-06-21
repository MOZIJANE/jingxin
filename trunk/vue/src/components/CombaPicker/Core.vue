<template>
  <div class="comba-picker-core">
    <div class="comba-picker-core-default">
      <el-radio-group v-model="label" :size="size">
        <el-radio-button label="日"></el-radio-button>
        <el-radio-button label="周"></el-radio-button>
        <el-radio-button label="月"></el-radio-button>
        <el-radio-button label="年"></el-radio-button>
      </el-radio-group>
      <el-button :size="size" icon="el-icon-arrow-left" @click="handleUpDownDate(-1)"></el-button>
      <el-date-picker :size="size" :key="formatter.type" v-model="value" :picker-options="pickerOptions" :type="formatter.type" :format="formatter.format" :placeholder="formatter.placeholder" :clearable="false">
      </el-date-picker>
      <el-button :size="size" icon="el-icon-arrow-right" @click="handleUpDownDate(1)"></el-button>
      <el-button :size="size" icon="el-icon-arrow-right" @click="changeToCustom">自定义</el-button>
    </div>
    <div class="comba-picker-core-customize">
      <el-date-picker
        key="custom"
        :size="size"
        v-model="rangeValue"
        :picker-options="pickerOptions"
        type="datetimerange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        :clearable="false"
      >
      </el-date-picker>
      <el-button :size="size" icon="el-icon-arrow-left" @click="changeToDefault">默认</el-button>
    </div>
  </div>
</template>

<script>
import shortcuts from './pickerOptions';

const oneDay = 1000 * 60 * 60 * 24;
const now = new Date();
const today = [
  new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0),
  new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59),
];

export default {
  name: 'comba-picker-core',
  props: {
    size: {
      type: String,
      default: 'mini',
    },
  },
  data() {
    return {
      customize: false,
      label: '日',
      pickerOptions: {
        firstDayOfWeek: 1,
        shortcuts: this.shortcuts,
      },
      value: now,
      rangeValue: today,
    };
  },
  computed: {
    formatter() {
      const { label } = this;
      if (label === '日') {
        return { type: 'date', format: '', placeholder: '选择日', step: 1 };
      }
      if (label === '周') {
        return { type: 'week', format: 'yyyy 第 WW 周', placeholder: '选择周', step: 7 };
      }
      if (label === '月') {
        return { type: 'month', format: 'yyyy 年 MM 月', placeholder: '选择月', step: 30 };
      }
      return { type: 'year', format: 'yyyy 年', placeholder: '选择年', step: 365 };
    },
    shortcuts() {
      return this.customize ? shortcuts : [];
    },
  },
  methods: {
    handleUpDownDate(direction) {
      const { value, formatter } = this;
      if (value !== '') {
        this.value = new Date((new Date(value).getTime()) + direction * oneDay * formatter.step);
      }
    },
    changeToDefault() {
      this.customize = false;
    },
    changeToCustom() {
      this.customize = true;
    },
  },
};
</script>

