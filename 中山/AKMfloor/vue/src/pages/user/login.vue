<template>
  <div class="login-wrapper">
    <el-card>
      <h1 class="login-title">智能云登录</h1>
      <el-form ref="loginForm" :model="loginForm" :rules="loginRules">
        <el-form-item prop="user">
          <el-input v-model="loginForm.user" placeholder="请输入账号" clearable></el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" clearable @keyup.enter.native="login"></el-input>
        </el-form-item>
        <el-row class="clearfix">
          <el-col :span="12" class="pull-left">
            <el-checkbox v-model="checked">自动登陆</el-checkbox>
          </el-col>
          <el-col :span="12" class="pull-right">
            <router-link to="/">
              <!-- <el-button size="mini" type="text">忘记密码</el-button> -->
            </router-link>
          </el-col>
        </el-row>
        <el-button class="form-item" type="primary" @click="login">登陆</el-button>
      </el-form>
      <el-row class="clear-fix">
        <el-col :span="12" class="pull-left"></el-col>
        <el-col :span="12" class="pull-right">
          <router-link :to="'/' + $route.params.domain + '/user/register'">
            <!-- <el-button size="mini" type="text">注册账号</el-button> -->
          </router-link>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script>
import { Message } from 'element-ui';

export default {
  title: '京信智能 - 登录',
  data() {
    return {
      checked: false,
      loginForm: {
        user: '',
        password: '',
      },
      loginRules: {
        user: [
          { required: true, message: '请输入账号', trigger: 'blur' },
          {
            type: 'string',
            min: 2,
            message: '长度在 6 个字符以上',
            trigger: 'blur',
          },
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          // eslint-disable-next-line
          { min: 6, max: 20, message: '长度在 6 至 20 个字符', trigger: 'blur' }
        ],
      },
    };
  },
  methods: {
    login() {
      const domain = location.pathname.split('/')[1];
      // const { domain } = this.$route.params;
      const { user, password } = this.loginForm;
      this.$refs.loginForm.validate((valid) => {
        if (!valid) {
          return Message({
            message: '请输入正确的账号&密码',
            type: 'error',
            showClose: true,
            duration: 2 * 1000,
          });
        }
        return this.$store.dispatch('Login', { user, password, domain });
      });
    },
  },
};
</script>

<style lang="scss" scoped>
.login-wrapper {
  position: absolute;
  transform: translate(-50%, -50%);
  top: 50%;
  right: 2%;
  width: 25%;
  min-width: 300px;
  max-width: 360px;
  padding: 0 0.4rem;
  text-align: center;
  .login-title {
    font-size: 2.2rem;
    font-weight: bold;
    margin-bottom: 1rem;
    color: #232323;
  }
  .form-item {
    margin-bottom: 0.6rem;
    width: 100%;
  }
  .pull-left {
    float: left;
    text-align: left;
  }
  .pull-right {
    float: right;
    text-align: right;
  }
}
</style>
