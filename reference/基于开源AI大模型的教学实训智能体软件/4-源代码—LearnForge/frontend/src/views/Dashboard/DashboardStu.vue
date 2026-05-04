<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-toolbar-title>学生后台管理系统</v-toolbar-title>
    </v-app-bar>

    <v-navigation-drawer v-model="drawer">
      <v-sheet class="pa-4" color="grey-4">
        <v-container style="height: 100px" fluid>
          <v-row justify="center">
            <v-menu min-width="100px" rounded>
              <template v-slot:activator="{ props }">
                <v-btn icon v-bind="props">
                  <v-avatar color="blue" size="80">
                    <span class="text-h5">{{ user.initials }}</span>
                  </v-avatar>
                </v-btn>
              </template>
              <!-- <v-card>
                <v-card-text>
                  <div class="mx-auto text-center">
                    <v-avatar color="blue">
                      <span class="text-h5">{{ user.initials }}</span>
                    </v-avatar>
                    <h3>{{ user.fullName }}</h3>
                    <v-divider class="my-3"></v-divider>
                    <v-btn variant="text" rounded @click="login">登录</v-btn>
                    <v-btn variant="text" rounded @click="logout">登出</v-btn>
                  </div>
                </v-card-text>
              </v-card> -->
            </v-menu>
          </v-row>
        </v-container>

        <div>后台管理系统</div>
      </v-sheet>

      <v-divider></v-divider>

      <v-list>
        <v-list-item v-for="[icon, text, to] in links" :key="icon" :prepend-icon="icon" :title="text" link
          :to="{ name: to }" color="primary" rounded="xl"></v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-main>
      <v-container class="py-8 px-6" fluid>
        <router-view></router-view>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, computed, getCurrentInstance } from 'vue';

const drawer = ref(true);
const rawlinks = ref([
  ['mdi-draw', '我的任务', 'GetStudetActivity'],
  ['mdi-xml', '主页', 'StudentArea'],
  // ['mdi-playlist-star', '作业', 'DataDashboardStu'],
]);
const theme = ref('light');
const toggleTheme = () => theme.value = theme.value === 'light' ? 'dark' : 'light';
const username = ref(localStorage.getItem('username') || '');
const password = ref(localStorage.getItem('password') || '');
const tag = ref(localStorage.getItem('tag') || '');
const backendUrl = getCurrentInstance().appContext.config.globalProperties.$backendUrl;

// 计算属性来根据 tag 的值过滤 links 数组
const links = computed(() => {
  if (tag.value === 'student') {
    // 如果 tag 为 'student'，只保留符合条件的链接
    return rawlinks.value.filter(link => link[2] !== 'ExamDesign');
  } else {
    // 其他情况下返回原始 links 数组
    return rawlinks.value;
  }
});
</script>

<script>
export default {
  data() {
    return {
      dark: false,
      isAuthenticated: false,
    };
  },
  created() {
    this.checkAuth();
  },
  methods: {
    login() {
      this.checkAuth();
      this.$router.push({ name: 'Login' });
    },
    logout() {
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      localStorage.removeItem('password');
      localStorage.removeItem('tag');
      this.checkAuth();
      this.$router.push({ name: 'Login' });
    },
    checkAuth() {
      this.isAuthenticated = !!localStorage.getItem('token');
    },
    toggleTheme() {
      this.dark = !this.dark;
      this.$vuetify.theme.dark = this.dark;
    }
  },
  computed: {
    dayNightModeIcon() {
      return this.dark ? 'mdi-weather-night' : 'mdi-weather-sunny';
    },
    user() {
      if (this.isAuthenticated) {
        const username = localStorage.getItem('realname');
        if (username) {
          return {
            initials: username.charAt(0),
            fullName: username,
            color: 'primary'
          };
        }
      }

      // 如果出现错误或未登录，则返回默认用户对象
      return {
        initials: '未',
        fullName: '未登录',
        color: 'grey lighten-1'
      };
    }
  }
}
</script>

<style>
/* 添加自定义样式 */
</style>
