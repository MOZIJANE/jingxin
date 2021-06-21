<template>
  <el-row :gutter="4" class="el-row">
    <el-col :span="12" class="error-image">
      <span>
        <img :src="image" alt="">
      </span>
    </el-col>
    <el-col :span="12" class="error-message">
      <h1>{{code}}</h1>
      <p>{{message}}</p>
      <el-button type="primary">返回首页</el-button>
    </el-col>
  </el-row>
</template>

<script>
import { codeMessage } from '@/request';

export default {
  name: 'comba-error',
  props: {
    code: {
      type: Number,
      default: 404,
    },
  },
  data() {
    return {};
  },
  computed: {
    message() {
      return codeMessage[this.code];
    },
    image() {
      return `/images/error/${this.code}.svg`;
    },
  },
};
</script>

<style lang="scss" scoped>
.error-image {
  min-width: 320px;
  min-height: 480px;
  padding-left: 40px;
  text-align: center;
  display: table;
  span {
    display: table-cell;
    vertical-align: middle;
    width: 100%;
  }
  > img {
    width: 100%;
  }
}
.error-message {
  line-height: 1rem;
  > h1 {
    font-size: 6rem;
    font-weight: 700;
  }
  > p {
    font-size: 1.2rem;
  }
}
</style>

