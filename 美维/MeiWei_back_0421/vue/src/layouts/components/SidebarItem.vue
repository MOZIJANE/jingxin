<template>
  <div class="menu-wrapper">
    <template v-for="item in menu" v-if="!item.hidden&&item.children">
      <el-submenu :index="item.name||item.path" :key="item.name">
        <template slot="title">
          <icon v-if="item&&item.icon" :name="item.icon"></icon>
          <span v-if="item&&item.title">{{item.title}}</span>
        </template>

        <template v-for="child in item.children" v-if="!child.hidden">
          <sidebar-item :is-nest="true" class="nest-menu" v-if="child.children&&child.children.length>0" :menu="[child]" :key="child.name"></sidebar-item>
          <template v-else>
            <template v-if="child.redirect">
              <el-menu-item :index="item.path+'/'+child.path" :key="child.redirect">
                <a :href="redirectPath(child.redirect)" target="_blank">
                  <icon v-if="child&&child.icon" :name="child.icon"></icon>
                  <span v-if="child&&child.title">{{child.title}}</span>
                </a>
              </el-menu-item>
            </template>
            <router-link v-else :to="child.path" :key="child.name">
              <el-menu-item :index="item.path+'/'+child.path">
                <icon v-if="child&&child.icon" :name="child.icon"></icon>
                <span v-if="child&&child.title">{{child.title}}</span>
              </el-menu-item>
            </router-link>
          </template>
        </template>
      </el-submenu>

    </template>
  </div>
</template>

<script>
import { isUrl } from '@/utils/utils';

export default {
  name: 'sidebar-item',
  props: {
    menu: {
      type: Array,
    },
    isNest: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    isUrl,
    redirectPath(redirect) {
      const result = this.isUrl(redirect)
        ? redirect
        : `http://${location.hostname}:${Number(location.port) - 1}${redirect}`;
      return result;
    },
  },
};
</script>

