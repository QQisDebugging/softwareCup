<template>
  <v-app id="inspire" :theme="theme">
    <!-- 现代化导航栏 -->
    <v-app-bar 
      v-if="showDrawer" 
      :elevation="0" 
      class="modern-app-bar"
      color="transparent"
      height="72"
    >
      <!-- 导航栏内容 -->
      <div class="app-bar-content">
        <!-- 左侧：菜单按钮和品牌 -->
        <div class="app-bar-left">
          <v-app-bar-nav-icon 
            @click="drawer = !drawer"
            class="nav-toggle-btn"
          />
          <div class="brand-section">
            <img 
              src="@/assets/logo/logo_thinborder.png" 
              alt="LearnForge" 
              class="brand-logo"
            />
            <span class="brand-name">LearnForge</span>
          </div>
        </div>

        <!-- 右侧：操作按钮 -->
        <div class="app-bar-right">
          <!-- 消息通知 -->
          <v-badge
            v-if="tag === 'student'"
            :content="messages.length"
            :model-value="messages.length > 0"
            color="error"
            class="message-badge"
          >
            <v-btn
              icon
              @click="toggleMessages"
              class="action-btn"
              size="large"
            >
              <v-icon>mdi-bell</v-icon>
            </v-btn>
          </v-badge>

          <!-- 主题切换 -->
          <v-btn
            icon
            @click="toggleTheme"
            class="action-btn theme-toggle"
            size="large"
          >
            <v-icon>{{ dayNightModeIcon }}</v-icon>
          </v-btn>

          <!-- 用户头像 -->
          <v-menu min-width="280px" offset-y class="user-menu">
            <template v-slot:activator="{ props }">
              <v-btn
                class="user-avatar-btn"
                v-bind="props"
              >
                <v-avatar size="40" class="user-avatar">
                  <span class="avatar-text">{{ user.initials }}</span>
                </v-avatar>
              </v-btn>
            </template>
            
            <v-card class="user-menu-card">
              <v-card-text class="user-menu-content">
                <div class="user-info">
                  <v-avatar size="60" class="user-menu-avatar">
                    <span class="avatar-text">{{ user.initials }}</span>
                  </v-avatar>
                  <div class="user-details">
                    <h3 class="user-name">{{ user.fullName }}</h3>
                    <p class="user-role">{{ tag === 'student' ? '学生' : '教师' }}</p>
                  </div>
                </div>
                
                <v-divider class="my-4" />
                
                <div class="menu-actions">
                  <v-btn
                    variant="tonal"
                    color="primary"
                    @click="navigateToProfile"
                    block
                    class="mb-2"
                  >
                    <v-icon left>mdi-account</v-icon>
                    个人资料
                  </v-btn>
                  
                  <v-btn
                    variant="outlined"
                    @click="logout"
                    block
                    color="error"
                  >
                    <v-icon left>mdi-logout</v-icon>
                    退出登录
                  </v-btn>
                </div>
              </v-card-text>
            </v-card>
          </v-menu>
        </div>
      </div>
    </v-app-bar>

    <!-- 现代化导航抽屉 -->
    <v-navigation-drawer 
      v-if="showDrawer" 
      v-model="drawer"
      class="modern-nav-drawer"
      :width="280"
    >
      <!-- 头部区域 -->
      <div class="nav-header">
        <div class="nav-header-content">
          <div class="welcome-section">
            <div class="welcome-icon">
              <v-icon size="32" color="primary">mdi-school</v-icon>
            </div>
            <div class="welcome-text">
              <h3>欢迎来到</h3>
              <h2 class="gradient-text">LearnForge</h2>
              <p>智能学习，创造未来</p>
            </div>
          </div>
        </div>
      </div>

      <v-divider class="nav-divider" />

      <!-- 导航列表 -->
      <div class="nav-content">
        <!-- 主要功能 -->
        <div class="nav-section">
          <h4 class="nav-section-title">主要功能</h4>
          <v-list class="nav-list">
            <v-list-item
              v-for="[icon, text, to] in links"
              :key="icon"
              :prepend-icon="icon"
              :title="text"
              :to="{ name: to }"
              class="nav-item modern-nav-item"
              color="primary"
              rounded="xl"
            />
          </v-list>
        </div>

        <!-- 其他功能 -->
        <div class="nav-section">
          <h4 class="nav-section-title">其他</h4>
          <v-list class="nav-list">
            <v-list-item
              v-for="[icon, text, to] in otherlinks"
              :key="icon"
              :prepend-icon="icon"
              :title="text"
              :to="{ name: to }"
              class="nav-item modern-nav-item"
              color="primary"
              rounded="xl"
            />
          </v-list>
        </div>
      </div>
    </v-navigation-drawer>

    <!-- 消息抽屉 -->
    <v-navigation-drawer
      location="right"
      temporary
      v-model="showMessages"
      :width="360"
      class="messages-drawer"
    >
      <div class="messages-header">
        <h3 class="messages-title">消息通知</h3>
        <v-btn
          icon
          @click="showMessages = false"
          class="close-btn"
          size="small"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </div>

      <v-divider />

      <div class="messages-content">
        <div v-if="messages.length > 0" class="messages-list">
          <div 
            v-for="(message, index) in messages" 
            :key="index"
            class="message-item"
          >
            <v-avatar size="44" class="message-avatar">
              <span v-if="message.type === 'teacher'">
                {{ message.sender_name[0] }}
              </span>
              <span v-else>
                {{ message.partner_name[0] }}
              </span>
            </v-avatar>

            <div class="message-content">
              <div class="message-header">
                <h4 v-if="message.type === 'teacher'">
                  {{ message.sender_name }}
                </h4>
                <h4 v-else>
                  {{ message.partner_name }}
                </h4>
                <span class="message-time">刚刚</span>
              </div>
              
              <p class="message-text" @click="showFullMessage(message.content)">
                <span v-if="message.type === 'teacher'">
                  {{ message.content }}
                </span>
                <span v-else>
                  {{ message.show }}
                </span>
              </p>

              <v-btn
                v-if="message.type === 'student'"
                variant="text"
                size="small"
                color="primary"
                @click="toggleChat(message.sender_sno, message.receiver_sno, message.partner_name)"
              >
                <v-icon left size="16">mdi-reply</v-icon>
                回复
              </v-btn>
            </div>
          </div>
        </div>

        <v-empty-state
          v-else
          title="暂无新消息"
          text="当有新消息时，会在这里显示"
          image="https://vuetifyjs.b-cdn.net/docs/images/components/v-empty-state/astro-cat.svg"
          class="empty-messages"
        />
      </div>
    </v-navigation-drawer>

    <!-- 聊天对话框 -->
    <v-dialog 
      v-model="showChat" 
      persistent 
      max-width="600"
      class="chat-dialog"
    >
      <v-card class="chat-card">
        <v-card-title class="chat-header">
          <div class="chat-header-content">
            <div class="chat-user-info">
              <v-avatar size="40" color="primary">
                <span>{{ activeChatMessages.partner_name?.[0] }}</span>
              </v-avatar>
              <div class="chat-user-details">
                <h4>{{ activeChatMessages.partner_name }}</h4>
                <span class="chat-status">在线</span>
              </div>
            </div>
            
            <div class="chat-actions">
              <v-btn
                icon
                @click="goToHomePage(String(activeChatMessages.receiver) === myself ? activeChatMessages.sender : activeChatMessages.receiver)"
                size="small"
              >
                <v-icon>mdi-account</v-icon>
              </v-btn>
              <v-btn
                icon
                @click="showChat = false"
                size="small"
              >
                <v-icon>mdi-close</v-icon>
              </v-btn>
            </div>
          </div>
        </v-card-title>

        <v-divider />

        <v-card-text class="chat-content">
          <div class="chat-messages">
            <div
              v-for="(message, index) in activeChatMessages.messages"
              :key="index"
              :class="['chat-message', message.from == myself ? 'own-message' : 'other-message']"
            >
              <div class="message-bubble" :class="user_currentMode">
                {{ message.content }}
              </div>
              <div class="message-time">
                {{ formatTime(message.timestamp) }}
              </div>
            </div>
          </div>
        </v-card-text>

        <v-divider />

        <v-card-actions class="chat-input-area">
          <v-text-field
            v-model="newMessage"
            placeholder="输入消息..."
            variant="outlined"
            @keyup.enter="sendMessage"
            class="chat-input"
            hide-details
            density="comfortable"
          >
            <template v-slot:append-inner>
              <v-btn
                icon
                @click="sendMessage"
                color="primary"
                size="small"
              >
                <v-icon>mdi-send</v-icon>
              </v-btn>
            </template>
          </v-text-field>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 消息详情对话框 -->
    <v-dialog v-model="dialogVisible" max-width="500">
      <v-card class="message-detail-card">
        <v-card-title class="message-detail-title">
          <v-icon left color="primary">mdi-message-text</v-icon>
          通知详情
        </v-card-title>
        
        <v-card-text class="message-detail-content">
          {{ dialogContent }}
        </v-card-text>
        
        <v-card-actions class="message-detail-actions">
          <v-spacer />
          <v-btn
            color="primary"
            variant="tonal"
            @click="dialogVisible = false"
          >
            <v-icon left>mdi-check</v-icon>
            已阅
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 主要内容区域 -->
    <v-main class="main-content">
      <router-view v-slot="{ Component, route }">
        <keep-alive :include="shouldKeepAlive(route)">
          <component :is="Component" @start-chat="handleStartChat" />
        </keep-alive>
      </router-view>
    </v-main>
    
    <!-- Toast组件 -->
    <Toast ref="toast" />
  </v-app>
</template>

<script setup>
import axios from "axios";
import { ref, reactive, computed, getCurrentInstance } from "vue";
import Toast from '@/components/Toast.vue';

const emit = defineEmits(["startChat"]);

function handleStartChat(sender, receiver) {
  createChat(sender, receiver);
}

// Dialog state
const dialogVisible = ref(false);
const dialogContent = ref("");

// Method to show the full message content
function showFullMessage(content) {
  dialogContent.value = content;
  dialogVisible.value = true;
}

const theme = ref(localStorage.getItem("theme") || "light");
const toggleTheme = () => {
  theme.value = theme.value === "light" ? "dark" : "light";
  localStorage.setItem("theme", theme.value);
};

const dayNightModeIcon = computed(() => {
  return theme.value !== "light" ? "mdi-weather-night" : "mdi-weather-sunny";
});

// Computed property to determine the current theme mode
const user_currentMode = computed(() =>
  theme.value === "light"
    ? "light-user-message-content"
    : "dark-user-message-content"
);
const other_currentMode = computed(() =>
  theme.value === "light"
    ? "light-other-message-content"
    : "dark-other-message-content"
);

const rawlinks = ref([
  ["mdi-home", "我的主页", "StudentAccount"],
  ["mdi-code-tags", "我的实训", "GetStudetWork"],
  ["mdi-clipboard-text", "我的任务", "GetStudetActivity"],
  ["mdi-trophy", "我的作业", "GetStudetContest"],
  ["mdi-tools", "学生工具", "StudentArea"],
  ["mdi-school", "教师工具", "TeacherArea"],
  ["mdi-chart-line", "排行榜", "StudyRank"],
]);

const others = ref([
  ["mdi-cog", "后台管理", "DashboardTea"],
  ["mdi-information", "关于", "Profile"],
]);

const chatMessages = ref();
const drawer = ref(true);
const showMessages = ref(false);
const showChat = ref(false);
const activeChatMessages = reactive({
  messages: [],
});
const newMessage = ref("");
const hasNew = ref(false);
const myself = localStorage.getItem("username");
const password = ref(localStorage.getItem("password") || "");
const tag = ref(localStorage.getItem("tag") || "");
const backendUrl = getCurrentInstance().appContext.config.globalProperties.$backendUrl;

// 计算属性来根据 tag 的值过滤 links 数组
const links = computed(() => {
  if (tag.value === "student") {
    return rawlinks.value.filter((link) => link[2] !== "TeacherArea");
  } else if (tag.value === "teacher") {
    return rawlinks.value.filter(
      (link) =>
        link[2] !== "StudentAccount" &&
        link[2] !== "GetStudetActivity" &&
        link[2] !== "GetStudetWork" &&
        link[2] !== "GetStudetContest"
    );
  } else {
    return rawlinks.value;
  }
});

const otherlinks = computed(() => {
  if (tag.value === "student") {
    return others.value.filter((link) => link[2] !== "DashboardTea");
  } else {
    return others.value;
  }
});

const messages = ref([]);

const toggleMessages = async () => {
  showMessages.value = !showMessages.value;
  if (showMessages.value) {
    await fetchMessages();
  }
};

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return "";
  const date = new Date(timestamp);
  return date.toLocaleTimeString();
};

// 发送消息
const sendMessage = async () => {
  if (!newMessage.value.trim()) return;
  
  try {
    // 这里应该调用实际的发送消息API
    const messageData = {
      content: newMessage.value,
      from: myself,
      to: activeChatMessages.receiver === myself ? activeChatMessages.sender : activeChatMessages.receiver,
      timestamp: new Date().toISOString()
    };
    
    // 添加到本地消息列表
    activeChatMessages.messages.push({
      content: newMessage.value,
      from: myself,
      timestamp: new Date().toISOString()
    });
    
    newMessage.value = "";
  } catch (error) {
    console.error("发送消息失败:", error);
  }
};

// 创建聊天
const createChat = (sender, receiver) => {
  activeChatMessages.sender = sender;
  activeChatMessages.receiver = receiver;
  activeChatMessages.messages = [];
  showChat.value = true;
  refresh(sender, receiver);
};

// 切换聊天
const toggleChat = (sender, receiver, partnerName) => {
  activeChatMessages.sender = sender;
  activeChatMessages.receiver = receiver;
  activeChatMessages.partner_name = partnerName;
  activeChatMessages.messages = [];
  showChat.value = true;
  showMessages.value = false;
  refresh(sender, receiver);
};

// 获取消息
const fetchMessages = async () => {
  try {
    const response = await axios.post(`${backendUrl}/api/messages`, {
      sno: localStorage.getItem("sno"),
    });
    messages.value = response.data || [];
  } catch (error) {
    console.error("获取消息数据失败:", error);
  }
};

// 刷新聊天记录
const refresh = async (sender, receiver) => {
  try {
    const response = await axios.get(`${backendUrl}/api/fetchMessages`, {
      params: { sender: sender, receiver: receiver },
    });
    activeChatMessages.messages = response.data.messages || [];
  } catch (error) {
    console.error("获取聊天记录失败:", error);
  }
};

// 初始化
fetchMessages();
</script>

<script>
import axios from "axios";

export default {
  data() {
    return {
      rail: true,
      dark: false,
      isAuthenticated: false,
    };
  },
  created() {
    this.checkAuth();
  },
  methods: {
    goToHomePage(studentId) {
      this.$router.push({ name: "User", params: { user_id: studentId } });
    },

    navigateToProfile() {
      const tag = localStorage.getItem("tag");
      if (tag === "student") {
        this.$router.push({ name: "StudentAccount" });
      } else {
        this.$router.push({ name: "DashboardTea" });
      }
    },

    checkAuth() {
      this.isAuthenticated = !!localStorage.getItem("token");
    },

    login() {
      this.checkAuth();
      this.$router.push({ name: "Login" });
    },

    async logout() {
      try {
        const response = await axios.post(`${this.$backendUrl}/api/logout`, {}, {});
        if (response.data.success) {
          localStorage.removeItem("token");
          localStorage.removeItem("username");
          localStorage.removeItem("password");
          localStorage.removeItem("tag");
          this.checkAuth();
          this.$router.push({ name: "Login" });
        }
      } catch (error) {
        console.log("Logout failed: " + error);
      }
    },

    shouldKeepAlive(route) {
      return route.meta.keepAlive ? [route.name] : [];
    },
  },
  
  computed: {
    showDrawer() {
      return !this.$route.meta.hideDrawer;
    },
    user() {
      if (this.isAuthenticated) {
        const username = localStorage.getItem("realname");
        if (username) {
          return {
            initials: username.charAt(0),
            fullName: username,
            color: "primary",
          };
        }
      }
      return {
        initials: "未",
        fullName: "未登录",
        color: "grey lighten-1",
      };
    },
  },
};
</script>

<style scoped>
/* 现代化应用栏 */
.modern-app-bar {
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.9) !important;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

[data-theme="dark"] .modern-app-bar {
  background: rgba(18, 18, 18, 0.9) !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
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

.brand-logo {
  width: 36px;
  height: 36px;
  object-fit: contain;
}

.brand-name {
  font-size: 1.25rem;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
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
  background: rgba(102, 126, 234, 0.1);
  transform: translateY(-1px);
}

.message-badge {
  position: relative;
}

.user-avatar-btn {
  border-radius: 50%;
  padding: 4px;
  min-width: auto;
  height: auto;
}

.user-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.avatar-text {
  color: white;
  font-weight: 600;
}

/* 用户菜单增强 */
.user-menu-card {
  border-radius: 20px;
  box-shadow: 0 15px 40px rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.1);
  overflow: hidden;
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.95);
  position: relative;
}

.user-menu-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 200% 100%;
  animation: gradientFlow 3s ease-in-out infinite;
}

@keyframes gradientFlow {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

[data-theme="dark"] .user-menu-card {
  background: rgba(30, 30, 40, 0.95);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
}

.user-menu-content {
  padding: 2rem;
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.user-info:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: translateY(-2px);
}

.user-menu-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 700;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  position: relative;
  overflow: hidden;
}

.user-menu-avatar::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transform: rotate(45deg);
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
  100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

[data-theme="dark"] .user-name {
  background: linear-gradient(135deg, #f7fafc 0%, #e2e8f0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.user-role {
  font-size: 0.9rem;
  opacity: 0.7;
  margin: 0;
  padding: 0.25rem 0.75rem;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 20px;
  display: inline-block;
  font-weight: 500;
}

.menu-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.menu-actions .v-btn {
  border-radius: 16px;
  text-transform: none;
  font-weight: 600;
  padding: 0.75rem 1.5rem;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  position: relative;
  overflow: hidden;
}

.menu-actions .v-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.menu-actions .v-btn:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.25);
}

.menu-actions .v-btn:hover::before {
  left: 100%;
}

/* 现代化导航抽屉增强 */
.modern-nav-drawer {
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
  border-right: 1px solid rgba(102, 126, 234, 0.1);
  box-shadow: 4px 0 20px rgba(102, 126, 234, 0.05);
  position: relative;
  overflow: hidden;
}

.modern-nav-drawer::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 3px;
  height: 100%;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 100% 200%;
  animation: gradientSlide 4s ease-in-out infinite;
}

@keyframes gradientSlide {
  0%, 100% { background-position: 0% 0%; }
  50% { background-position: 0% 100%; }
}

[data-theme="dark"] .modern-nav-drawer {
  background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.3);
}

.nav-header {
  padding: 2.5rem 1.5rem 1.5rem;
  position: relative;
  overflow: hidden;
}

.nav-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 50% 0%, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
}

.nav-header-content {
  text-align: center;
  position: relative;
  z-index: 2;
}

.welcome-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.welcome-icon {
  width: 72px;
  height: 72px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.welcome-icon::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.2) 0%, transparent 70%);
  animation: iconPulse 4s ease-in-out infinite;
}

@keyframes iconPulse {
  0%, 100% { transform: scale(0.8) rotate(0deg); opacity: 0.5; }
  50% { transform: scale(1.2) rotate(180deg); opacity: 1; }
}

.welcome-icon:hover {
  transform: scale(1.1) rotateY(15deg);
  box-shadow: 0 12px 30px rgba(102, 126, 234, 0.5);
}

.welcome-text h3 {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0;
  opacity: 0.8;
  letter-spacing: 0.5px;
}

.welcome-text h2 {
  font-size: 1.8rem;
  font-weight: 900;
  margin: 0.5rem 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
}

.welcome-text p {
  font-size: 0.85rem;
  margin: 0;
  opacity: 0.7;
  font-weight: 500;
}

.nav-divider {
  margin: 0 1.5rem;
  opacity: 0.4;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.3), transparent);
}

.nav-content {
  padding: 1.5rem;
}

.nav-section {
  margin-bottom: 2.5rem;
}

.nav-section-title {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin: 0 0 1.5rem 1rem;
  opacity: 0.7;
  color: #667eea;
  position: relative;
}

.nav-section-title::before {
  content: '';
  position: absolute;
  left: -1rem;
  top: 50%;
  width: 3px;
  height: 80%;
  background: linear-gradient(180deg, #667eea, #764ba2);
  border-radius: 2px;
  transform: translateY(-50%);
}

.nav-list {
  padding: 0;
}

.modern-nav-item {
  margin-bottom: 0.75rem;
  border-radius: 16px;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  position: relative;
  overflow: hidden;
}

.modern-nav-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
  transition: left 0.5s ease;
}

.modern-nav-item:hover {
  transform: translateX(8px) scale(1.02);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.25);
  background: rgba(102, 126, 234, 0.05);
}

.modern-nav-item:hover::before {
  left: 100%;
}

.modern-nav-item.v-list-item--active {
  background: rgba(102, 126, 234, 0.1) !important;
  color: #667eea !important;
  transform: translateX(4px);
}

.modern-nav-item.v-list-item--active::after {
  content: '';
  position: absolute;
  right: 0;
  top: 20%;
  width: 4px;
  height: 60%;
  background: linear-gradient(180deg, #667eea, #764ba2);
  border-radius: 2px 0 0 2px;
}

/* 消息抽屉 */
.messages-drawer {
  border-left: 1px solid rgba(0, 0, 0, 0.05);
}

.messages-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.messages-title {
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
}

.close-btn {
  color: white;
}

.messages-content {
  padding: 1rem;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  border-radius: 12px;
  background: rgba(102, 126, 234, 0.05);
  transition: all 0.2s ease;
}

.message-item:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: translateY(-2px);
}

.message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  flex-shrink: 0;
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.message-header h4 {
  font-size: 0.9rem;
  font-weight: 600;
  margin: 0;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.6;
}

.message-text {
  font-size: 0.85rem;
  line-height: 1.4;
  margin: 0 0 0.5rem 0;
  cursor: pointer;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.empty-messages {
  margin-top: 2rem;
}

/* 聊天对话框 */
.chat-dialog .v-overlay__content {
  margin: 2rem;
}

.chat-card {
  border-radius: 16px;
  overflow: hidden;
}

.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 1.5rem;
}

.chat-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.chat-user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.chat-user-details h4 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
}

.chat-status {
  font-size: 0.8rem;
  opacity: 0.8;
}

.chat-actions {
  display: flex;
  gap: 0.5rem;
}

.chat-content {
  height: 400px;
  overflow-y: auto;
  padding: 1rem;
}

.chat-messages {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chat-message {
  display: flex;
  flex-direction: column;
  max-width: 80%;
}

.own-message {
  align-self: flex-end;
  align-items: flex-end;
}

.other-message {
  align-self: flex-start;
  align-items: flex-start;
}

.message-bubble {
  padding: 0.75rem 1rem;
  border-radius: 16px;
  word-wrap: break-word;
  max-width: 100%;
}

.light-user-message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.dark-user-message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.light-other-message-content {
  background: #f1f5f9;
  color: #334155;
}

.dark-other-message-content {
  background: #334155;
  color: #f1f5f9;
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.6;
  margin-top: 0.25rem;
}

.chat-input-area {
  padding: 1rem 1.5rem;
  background: rgba(248, 250, 252, 0.5);
}

.chat-input {
  border-radius: 24px;
}

/* 消息详情对话框 */
.message-detail-card {
  border-radius: 16px;
}

.message-detail-title {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message-detail-content {
  padding: 2rem;
  line-height: 1.6;
}

.message-detail-actions {
  padding: 1rem 1.5rem;
}

/* 主要内容区域 */
.main-content {
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  min-height: 100vh;
}

[data-theme="dark"] .main-content {
  background: linear-gradient(135deg, #1a1a1a 0%, #121212 100%);
}

/* 响应式设计 */
@media (max-width: 960px) {
  .app-bar-content {
    padding: 0 0.5rem;
  }
  
  .brand-name {
    display: none;
  }
  
  .nav-header {
    padding: 1.5rem 1rem 0.5rem;
  }
  
  .welcome-icon {
    width: 48px;
    height: 48px;
  }
  
  .welcome-text h2 {
    font-size: 1.25rem;
  }
}

@media (max-width: 600px) {
  .chat-dialog .v-overlay__content {
    margin: 1rem;
  }
  
  .chat-content {
    height: 300px;
  }
  
  .message-bubble {
    max-width: 85%;
  }
}

/* 动画和性能优化 */
.modern-nav-item,
.action-btn,
.message-item {
  will-change: transform;
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 滚动条样式 */
.chat-content::-webkit-scrollbar,
.messages-content::-webkit-scrollbar {
  width: 6px;
}

.chat-content::-webkit-scrollbar-track,
.messages-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.chat-content::-webkit-scrollbar-thumb,
.messages-content::-webkit-scrollbar-thumb {
  background: rgba(102, 126, 234, 0.3);
  border-radius: 3px;
}

.chat-content::-webkit-scrollbar-thumb:hover,
.messages-content::-webkit-scrollbar-thumb:hover {
  background: rgba(102, 126, 234, 0.5);
}
</style>