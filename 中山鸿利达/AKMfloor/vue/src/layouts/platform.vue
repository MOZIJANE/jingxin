<template>
  <el-container class="el-container outter">
      <transition name="fade">
        <el-aside :width="asideWidth">
          <div v-if="sidebar.opened" class="logo-container" style="height: 96px;">
            <div class="logo">
              <img src="/static/img/logo.svg" width="160px" alt="">
            </div>
            <div class="logo-heading">兴森快捷</div>
          </div>
          <div
            v-else
            key="logo-container-small"
            class="logo-container"
            style="height: 40px; margin: 0px; paddingTop: 10px;"
          >
            <img src="/static/img/logo.svg" width="40px" alt="">
          </div>
          <el-menu
            @select="handleMenuSelect"
            :default-active="$store.state.app.activeMenuIndex"
            :unique-opened="true"
            :collapse="!sidebar.opened"
            background-color="#2a2f32"
            text-color="#fefefe"
            active-text-color="#00c1de"
            class="menu"
          >
            <sidebar-item
              :menu="$store.state.menu"
              :is-nest="true"
            >
            </sidebar-item>
          </el-menu>
        </el-aside>
      </transition>
      <el-container class="el-container main">
        <el-header class="el-header clearfix" height="48px">
          <div class="header-left">
            <hamburger :toggleClick="toggleSideBar" :isActive="sidebar.opened"></hamburger>
            <div class="title">{{ title }}</div>
          </div>
          <div class="header-right">
            <!-- <transition name="fade">
              <div class="search-bar" v-show="search.opened">
                <el-input size="mini"></el-input>
              </div>
            </transition>
            <div class="icon search">
              <i class="el-icon-search" @click="toggleSearchBar"></i>
            </div> -->
            <template v-for="{ level, count } in alarms">
              <navbar-alarm :key="level" :level="level" :count="count"></navbar-alarm>
            </template>
            <div class="avatar">
              <el-popover
                width="240"
                trigger="hover">
                <el-container class="el-container mini">
                  <el-header class="el-header mini">
                    <el-row :gutter="8">
                      <el-col :span="8">
                        <img src="/static/img/tony.png" width="36" height="36">
                        <br>
                        <span>{{name}}</span>
                      </el-col>
                      <el-col :span="16" class="user-info">
                        <span><i class="el-icon-tickets"></i> 兴森快捷</span>
                        <br>
                        <span><i class="el-icon-service"></i> {{name}}</span>
                        <br>
                        <span><i class="el-icon-message"></i> chenruitong@comba.cn</span>
                      </el-col>
                    </el-row>
                  </el-header>
                  <el-main class="el-main mini">
                    <el-row>
                      <el-col :span="8">
                        <div class="mini info-card">
                          <div class="info-card-body">
                            <div>
                              <icon name="address-card"></icon>
                            </div>
                            <div>详细</div>
                          </div>
                        </div>
                      </el-col>
                      <el-col :span="8">
                        <div class="mini info-card">
                          <div class="info-card-body">
                            <div>
                              <icon name="cogs"></icon>
                            </div>
                            <div>设置</div>
                          </div>
                        </div>
                      </el-col>
                      <el-col :span="8">
                        <div class="mini info-card">
                          <div class="info-card-body">
                            <div>
                              <icon name="envelope"></icon>
                            </div>
                            <div>消息</div>
                          </div>
                        </div>
                      </el-col>
                    </el-row>
                  </el-main>
                  <el-footer class="el-footer mini" height="32px" @click.native="logout">
                    <i class="el-icon-circle-close-outline"></i>
                    <span>退出平台</span>
                  </el-footer>
                </el-container>
                <img src="/static/img/tony.png"  slot="reference">
              </el-popover>
            </div>
          </div>
        </el-header>

        <el-main class="el-main">
          <router-view/>
        </el-main>
        <el-footer class="el-footer" height="48px">
          © {{new Date().getFullYear()}} {{company.name}}
        </el-footer>
      </el-container>
  </el-container>
</template>

<script>
import 'vue-awesome/icons';
import Logo from '@/components/Logo/FabricLogo';
import Hamburger from '@/components/Hamburger';
import { mapGetters } from 'vuex';
import { getAlarms } from '@/services';
import SidebarItem from './components/SidebarItem';
import NavbarAlarm from './components/NavbarAlarm';

export default {
  name: 'platform-layout',
  components: {
    Logo,
    Hamburger,
    SidebarItem,
    NavbarAlarm,
  },
  data() {
    return {
      title: '兴森快捷',
      company: {
        name: '兴森快捷',
      },
      search: {
        opened: false,
        content: '',
      },
      alarms: [
        { level: 'critical', label: '严重告警', count: 0 },
        { level: 'major', label: '重要告警', count: 0 },
        { level: 'minor', label: '普通告警', count: 0 },
        { level: 'warning', label: '普通提醒', count: 0 },
      ],
    };
  },
  computed: {
    ...mapGetters(['sidebar', 'avatar', 'name']),

    asideWidth() {
      return this.sidebar.opened ? '180px' : '48px';
    },
  },
  methods: {
    handleMenuSelect(key) {
      this.$store.commit('SET_ACTIVEMENUINDEX', key);
    },
    openSideBar() {
      setTimeout(() => {
        this.$store.commit('OPEN_SIDEBAR');
      }, 500);
    },
    closeSideBar() {
      setTimeout(() => {
        this.$store.commit('CLOSE_SIDEBAR');
      }, 500);
    },
    toggleSideBar() {
      this.$store.dispatch('ToggleSideBar');
    },
    toggleSearchBar() {
      this.search.opened = !this.search.opened;
    },
    logout() {
      this.$store.dispatch('LogOut');
    },
    setMenu() {
      this.$store.dispatch('SetMenu');
    },
    setAlarms() {
      getAlarms().then((res) => {
        const { data: { alarmInfo } } = res;
        this.alarms.forEach((alarm) => {
          /* eslint-disable no-param-reassign */
          alarm.count = alarmInfo.find(item => item.level === alarm.level).count;
        });
      });
    },
  },
  watch: {
    $route: {
      handler: 'setMenu',
      immediate: true,
    },
  },
  mounted() {
    this.alarmsInt = setInterval(() => this.setAlarms(), 3000);
  },
  destroyed() {
    clearInterval(this.alarmsInt);
  },
};
</script>


<style lang="scss">
@import "../element-variables.scss";

$--comba-color-black: #343434;
$--comba-color-black-light: #464646;
//sidebar
$menuBg: $--comba-color-black;
$subMenuBg: darken($--comba-color-black, 7%);
$menuHover: darken($--comba-color-black, 10%);
$fontFamily: Helvetica Neue, Helvetica, PingFang SC, Hiragino Sans GB,
  Microsoft YaHei, SimSun, sans-serif;

.el-menu a {
  color: #fefefe !important;
  text-decoration: none;
}
.clearfix {
  &:after {
    content: "";
    display: table;
    clear: both;
  }
}
.hamburger-wrapper {
  line-height: 36px;
  height: 36px;
  color: $--color-white !important;
  text-align: center;
  display: flex;
  flex-direction: row;
  justify-content: center;
}
.el-container {
  &.outter {
    background-color: #000;
    position: absolute;
    left: 0;
    top: 0;
    right: 0;
    min-height: 100vh;
    margin: 0;
    padding: 0;
  }
}

.el-header,
.el-aside {
  cursor: pointer;
  background-color: $--comba-color-black;
  color: $--color-white;
  line-height: 48px;
}
.el-header {
  background-color: #fefefe;
  color: $--comba-color-black;
  border-bottom-color: rgb(16, 17, 17);
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.05);
  padding-left: 0;
  text-align: center;
}
.el-footer {
  background-color: #e9eef3;
  color: $--comba-color-black;
  text-align: center;
  line-height: 48px;
}
.el-aside {
  // text-align: left;
  border: none;
  border-top: 1px solid $--comba-color-black-light;
  box-shadow: 0 0px 10px $--comba-color-black;
  overflow-x: hidden;
  .menu {
    border-top: 1px solid $--comba-color-black-light;
  }
}

.el-main {
  background-color: #e9eef3;
  color: #333;
}

.el-badge {
  line-height: 1rem;
}

.header-left {
  display: flex;
  flex-direction: row;
  float: left;
  > * {
    display: inline-block;
  }
  > .title {
    min-width: 100px;
  }
}
.header-right {
  float: right;
  display: flex;
  flex-direction: row;
  > * {
    display: inline-block;
    margin-right: 4px;
    &:hover {
      color: #00c1de;
    }
  }
  > search-bar {
    width: 160px;
  }
  > .icon {
    width: 6.2rem;
  }
  > .info {
    padding-left: 1rem;
    padding-right: 6px;
  }
  > .avatar {
    display: block;
    padding-left: 1.2rem;
    img {
      margin-top: 6px;
      width: 36px;
      height: 36px;
      border-radius: 50%;
    }
  }
}

.mini.el-container {
  position: relative;
  cursor: pointer;
  width: 100%;
  .el-header {
    font-size: 0.7rem;
    white-space: nowrap;
    .user-info {
      text-align: left;
    }
  }
  .el-header,
  .el-footer {
    background: transparent;
    color: #333;
    line-height: 1rem;
    border: none;
    box-shadow: none;
  }
  .el-footer {
    padding-top: 1rem;
    text-align: middle;
  }
  .el-main {
    background: transparent;
    color: #333;
    width: 100%;
    padding: 0;
    margin: 0;
    position: relative;
    line-height: 1rem;
    .el-row {
      margin-bottom: 0;
    }
  }
}
.mini.info-card {
  position: relative;
  padding: 10px;
  box-sizing: border-box;
  border: 1px solid rgba(255, 255, 255, 0.01);
  &:hover {
    background-color: #e9eef3;
    border: 1px solid #eee;
  }
  .info-card-body {
    text-align: center;
    width: 3rem;
    height: 2rem;
  }
}

.el-tab-pane {
  text-align: center;
}
.el-menu {
  border-right: none !important;
}

.el-submenu__title {
  padding-left: 10px !important;
}

.nest-menu .el-submenu__title {
  padding-left: 40px !important;
}

.el-menu--collapse .el-submenu > .el-submenu__title {
  svg {
    margin-right: 20px;
  }
  .el-submenu__icon-arrow.el-icon-arrow-right {
    display: none;
  }
}

// logo
.logo-container-small {
  width: 100%;
  height: 48px;
}
.logo-container {
  margin-top: 0.3rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 120px;
}

.logo {
  margin-bottom: -4rem;
}

.logo-left,
.logo-right {
  display: inline-block;
  position: relative;
}

@keyframes logo-anim-left {
  from {
    top: 0;
  }
  26% {
    top: 0;
  }
  29% {
    top: 7px;
  }
  40% {
    top: 0;
  }
}

@keyframes logo-anim-right {
  from {
    top: -45px;
  }
  25% {
    top: -50px;
  }
  30% {
    top: 7px;
  }
  40% {
    top: 0px;
  }
}

.logo-left {
  animation-duration: 2s;
  animation-name: logo-anim-left;
  animation-iteration-count: infinite;
}

.logo-right {
  animation-duration: 2s;
  animation-name: logo-anim-right;
  animation-iteration-count: infinite;
}

.logo-heading {
  font-size: 1rem;
  font-weight: 500;
}

// transition
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
</style>
