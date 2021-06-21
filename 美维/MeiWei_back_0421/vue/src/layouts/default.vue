<template>
  <el-container class="el-container--login-layout">
    <el-header class="el-header--login-layout">
       {{company.name}}
      <div class="pull-right">
        <el-button type="info">首页</el-button>
      </div>
    </el-header>
    <el-main class="el-main--login-layout">
      <div class="slogan--login-layout">
        <h1>京信智能助力企业数字化转型</h1>
        <p>
          依托京信云可靠和灵活的云计算基础设施和平台服务<br/>
          结合世界领先的企业级数据库和商务应用解决方案<br/>
          推动企业数字化管理，走向智能化的康庄大道<br/>
        </p>
      </div>
      <router-view/>
    </el-main>
    <el-footer class="el-footer--login-layout" height="160px">
      <p class="copyright">© {{new Date().getFullYear()}} {{company.name}}</p>
    </el-footer>
  </el-container>
</template>

<script>
export default {
  data() {
    return {
      company: {
        name: '兴森快捷',
      },
    };
  },
};
</script>


<style>
html {
  font-family: "Source Sans Pro", -apple-system, BlinkMacSystemFont, "Segoe UI",
    Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 16px;
  word-spacing: 1px;
  -ms-text-size-adjust: 100%;
  -webkit-text-size-adjust: 100%;
  -moz-osx-font-smoothing: grayscale;
  -webkit-font-smoothing: antialiased;
  box-sizing: border-box;
}
*,
*:before,
*:after {
  box-sizing: border-box;
  margin: 0;
}
.pull-right {
  float: right;
}
.el-container--login-layout {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  line-height: 60px;
  color: #fefefe;
  background-color: #1f2325 !important;
}
.el-header--login-layout {
  line-height: 60px;
  border-bottom: 1px solid #a1a1a1;
  text-align: left;
  color: #fefefe;
  background-color: #1f2325 !important;
}
.el-main--login-layout {
  line-height: 60px;
  color: #fefefe;
  position: relative;
  width: 100vw;
  height: 320px !important;
  background-color: #1f2325 !important;
  background-image: url(/static/img/bg-login.jpg);
  background-position: center center;
  background-size: cover;
  box-shadow: 0 2px 10px #272d41;
}
.slogan--login-layout {
  position: absolute;
  transform: translate(-50%, -50%);
  top: 40%;
  left: 30%;
}
.slogan--login-layout h1 {
  font-size: 2.4rem;
  font-weight: 500;
  line-height: 6rem;
}
.slogan--login-layout p {
  font-size: 0.9rem;
  font-weight: 300;
  line-height: 2rem;
}
.el-footer--login-layout {
  width: 100vw;
  background: #373d41;
  color: #888;
  text-align: center;
}
</style>
