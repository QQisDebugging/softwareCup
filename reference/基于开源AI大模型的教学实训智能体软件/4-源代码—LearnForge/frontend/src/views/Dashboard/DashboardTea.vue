<template>
  <v-app>
    <!-- 现代化应用栏 -->
    <v-app-bar 
      :elevation="2" 
      app 
      class="modern-app-bar"
      color="primary"
      dark
      height="70"
    >
      <div class="app-bar-content">
        <div class="app-bar-left">
          <v-btn 
            icon 
            @click="drawer = !drawer"
            class="nav-toggle-btn"
            size="large"
          >
            <v-icon>mdi-menu</v-icon>
          </v-btn>
          
          <div class="brand-section">
            <v-icon color="white" size="40" class="brand-icon">mdi-school</v-icon>
            <h2 class="brand-name">教师管理中心</h2>
          </div>
        </div>

        <div class="app-bar-right">
          <v-btn 
            icon 
            class="action-btn"
            @click="toggleTheme"
          >
            <v-icon>{{ dayNightModeIcon }}</v-icon>
          </v-btn>
          
          <v-menu min-width="300">
            <template v-slot:activator="{ props }">
              <v-btn 
                class="user-avatar-btn"
                v-bind="props"
              >
                <v-avatar 
                  class="user-avatar"
                  size="40"
                  color="white"
                >
                  <span class="avatar-text">{{ user.initials }}</span>
                </v-avatar>
              </v-btn>
            </template>
            
            <v-card class="user-menu-card">
              <div class="user-menu-content">
                <div class="user-info">
                  <v-avatar 
                    class="user-menu-avatar"
                    size="60"
                    color="primary"
                  >
                    <span class="text-h6">{{ user.initials }}</span>
                  </v-avatar>
                  <div class="user-details">
                    <h3 class="user-name">{{ user.fullName }}</h3>
                    <p class="user-role">教师账户</p>
                  </div>
                </div>
                
                <v-divider class="my-3"></v-divider>
                
                <div class="menu-actions">
                  <v-btn 
                    variant="text" 
                    prepend-icon="mdi-logout"
                    @click="logout"
                    color="error"
                    block
                  >
                    退出登录
                  </v-btn>
                </div>
              </div>
            </v-card>
          </v-menu>
        </div>
      </div>
    </v-app-bar>

    <!-- 现代化导航抽屉 -->
    <v-navigation-drawer 
      v-model="drawer"
      class="modern-nav-drawer"
      width="300"
    >
      <!-- 用户信息头部 -->
      <div class="nav-header">
        <div class="nav-header-content">
          <v-avatar 
            class="nav-avatar"
            size="80"
            color="white"
          >
            <span class="text-h4 primary--text">{{ user.initials }}</span>
          </v-avatar>
          <h3 class="nav-username">{{ user.fullName }}</h3>
          <p class="nav-welcome">教师管理后台</p>
        </div>
      </div>

      <v-divider></v-divider>

      <!-- 导航菜单 -->
      <v-list class="nav-list" nav>
        <!-- 数据分析 -->
        <v-list-item 
          prepend-icon="mdi-chart-line"
          title="数据分析"
          subtitle="网站使用统计"
          :to="{ name: 'DataAnalysis' }"
          color="primary" 
          rounded="xl"
          class="nav-item"
        >
          <template v-slot:append>
            <v-icon color="primary" size="small">mdi-chevron-right</v-icon>
          </template>
        </v-list-item>

        <!-- 学生管理 -->
        <v-list-item 
          prepend-icon="mdi-account-group"
          title="学生管理"
          subtitle="查看学生列表和排名"
          :to="{ name: 'StudentList' }"
          color="primary" 
          rounded="xl"
          class="nav-item"
        >
          <template v-slot:append>
            <v-icon color="primary" size="small">mdi-chevron-right</v-icon>
          </template>
        </v-list-item>

        <!-- 实训管理 -->
        <v-list-group value="Work" class="nav-group">
          <template v-slot:activator="{ props }">
            <v-list-item 
              v-bind="props" 
              title="实训管理" 
              subtitle="创建和管理实训项目"
              class="nav-item group-activator"
            >
              <template v-slot:prepend>
                <v-icon color="primary">mdi-laptop</v-icon>
              </template>
            </v-list-item>
          </template>

          <v-list-item 
            v-for="[icon, text, to] in workLink" 
            :key="text"
            :title="text" 
            :to="{ name: to }"
            color="primary" 
            rounded="xl"
            class="nav-subitem"
          >
            <template v-slot:prepend>
              <v-icon :icon="icon" size="20"></v-icon>
            </template>
          </v-list-item>
        </v-list-group>

        <!-- 任务管理 -->
        <v-list-group value="Activity" class="nav-group">
          <template v-slot:activator="{ props }">
            <v-list-item 
              v-bind="props" 
              title="任务管理" 
              subtitle="创建和管理学习任务"
              class="nav-item group-activator"
            >
              <template v-slot:prepend>
                <v-icon color="primary">mdi-clipboard-list</v-icon>
              </template>
            </v-list-item>
          </template>

          <v-list-item 
            v-for="[icon, text, to] in activityLink" 
            :key="text"
            :title="text" 
            :to="{ name: to }"
            color="primary" 
            rounded="xl"
            class="nav-subitem"
          >
            <template v-slot:prepend>
              <v-icon :icon="icon" size="20"></v-icon>
            </template>
          </v-list-item>
        </v-list-group>

        <!-- 作业管理 -->
        <v-list-group value="Contest" class="nav-group">
          <template v-slot:activator="{ props }">
            <v-list-item 
              v-bind="props" 
              title="作业管理" 
              subtitle="创建和管理课程作业"
              class="nav-item group-activator"
            >
              <template v-slot:prepend>
                <v-icon color="primary">mdi-file-document-edit</v-icon>
              </template>
            </v-list-item>
          </template>

          <v-list-item 
            v-for="[icon, text, to] in contestLink" 
            :key="text"
            :title="text" 
            :to="{ name: to }"
            color="primary" 
            rounded="xl"
            class="nav-subitem"
          >
            <template v-slot:prepend>
              <v-icon :icon="icon" size="20"></v-icon>
            </template>
          </v-list-item>
        </v-list-group>

        <v-divider class="my-3"></v-divider>

        <!-- 返回主页 -->
        <v-list-item 
          prepend-icon="mdi-home-variant"
          title="返回主页"
          subtitle="回到学生工具中心"
          :to="{ name: 'StudentArea' }"
          color="success" 
          rounded="xl"
          class="nav-item"
        >
          <template v-slot:append>
            <v-icon color="success" size="small">mdi-chevron-right</v-icon>
          </template>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <!-- 主要内容区域 -->
    <v-main class="modern-main">
      <div class="main-content">
        <router-view></router-view>
      </div>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, computed, getCurrentInstance } from 'vue';

const drawer = ref(true);

// 更新的菜单链接，使用正确的图标名称
const workLink = ref([
  ['mdi-plus-circle', '创建实训', 'CreateWork'],
  ['mdi-folder-open', '我的实训', 'GetTeacherWork'],
]);

const activityLink = ref([
  ['mdi-plus-circle-outline', '创建任务', 'CreateActivity'],
  ['mdi-format-list-bulleted', '我的任务', 'GetTeacherActivity'],
]);

const contestLink = ref([
  ['mdi-file-plus', '创建作业', 'CreateContest'],
  ['mdi-file-document-multiple', '我的作业', 'GetTeacherContest'],
]);

const theme = ref('light');
const toggleTheme = () => theme.value = theme.value === 'light' ? 'dark' : 'light';
const username = ref(localStorage.getItem('username') || '');
const password = ref(localStorage.getItem('password') || '');
const tag = ref(localStorage.getItem('tag') || '');
const backendUrl = getCurrentInstance().appContext.config.globalProperties.$backendUrl;
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

      return {
        initials: '未',
        fullName: '未登录',
        color: 'grey lighten-1'
      };
    }
  }
}
</script>

<style scoped>
/* 现代化应用栏 */
.modern-app-bar {
  box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
}

.app-bar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 1rem;
}

.app-bar-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-toggle-btn {
  border-radius: 12px;
  transition: all 0.2s ease;
}

.brand-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.brand-icon {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 8px;
}

.brand-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: white;
  margin: 0;
}

.app-bar-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.action-btn {
  border-radius: 12px;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-1px);
}

.user-avatar-btn {
  border-radius: 50%;
  padding: 4px;
  min-width: auto;
  height: auto;
}

.user-avatar {
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.avatar-text {
  color: #1976d2;
  font-weight: 600;
}

/* 用户菜单 */
.user-menu-card {
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.user-menu-content {
  padding: 1.5rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
}

.user-role {
  font-size: 0.9rem;
  opacity: 0.7;
  margin: 0;
}

.menu-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* 现代化导航抽屉 */
.modern-nav-drawer {
  background: #f8f9fa;
  border-right: 1px solid rgba(0, 0, 0, 0.05);
}

.nav-header {
  padding: 2rem 1.5rem 1rem;
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
  color: white;
}

.nav-header-content {
  text-align: center;
}

.nav-avatar {
  margin-bottom: 1rem;
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.nav-username {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
}

.nav-welcome {
  font-size: 0.9rem;
  opacity: 0.9;
  margin: 0;
}

/* 导航列表 */
.nav-list {
  padding: 1rem !important;
}

.nav-item {
  margin-bottom: 0.5rem;
  border-radius: 12px !important;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: rgba(25, 118, 210, 0.1) !important;
  transform: translateX(4px);
}

.nav-subitem {
  margin-left: 1rem;
  margin-bottom: 0.3rem;
  border-radius: 8px !important;
  transition: all 0.2s ease;
}

.nav-subitem:hover {
  background: rgba(25, 118, 210, 0.08) !important;
  transform: translateX(2px);
}

.nav-group {
  margin-bottom: 0.5rem;
}

.group-activator {
  font-weight: 600;
}

/* 主要内容区域 */
.modern-main {
  background: #f5f5f5;
  min-height: 100vh;
}

.main-content {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-bar-content {
    padding: 0 0.5rem;
  }
  
  .brand-name {
    font-size: 1rem;
  }
  
  .nav-header {
    padding: 1.5rem 1rem 0.75rem;
  }
  
  .main-content {
    padding: 1rem;
  }

  .modern-nav-drawer {
    width: 280px !important;
  }
}

/* 动画效果 */
.nav-item, .nav-subitem {
  animation: fadeInUp 0.3s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 确保图标显示 */
.v-icon {
  font-feature-settings: 'liga';
}
</style>
