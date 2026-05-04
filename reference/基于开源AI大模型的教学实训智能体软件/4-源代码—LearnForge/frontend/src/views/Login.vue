<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
      <div class="floating-particles"></div>
    </div>

    <!-- 主要内容区域 -->
    <div class="login-content">
      <!-- 左侧信息面板 -->
      <div class="info-panel">
        <div class="brand-section">
          <div class="logo-container">
            <img src="@/assets/logo/logo_thinborder.png" alt="LearnForge" class="brand-logo" />
          </div>
          <h1 class="brand-title">LearnForge</h1>
          <p class="brand-subtitle">智能学习平台，让编程学习更高效</p>
        </div>
        
        <div class="features-showcase">
          <div class="feature-item">
            <div class="feature-icon">
              <v-icon color="white" size="24">mdi-brain</v-icon>
            </div>
            <div class="feature-text">
              <h3>AI智能助手</h3>
              <p>个性化学习建议</p>
            </div>
          </div>
          
          <div class="feature-item">
            <div class="feature-icon">
              <v-icon color="white" size="24">mdi-code-tags</v-icon>
            </div>
            <div class="feature-text">
              <h3>代码智能分析</h3>
              <p>实时代码优化建议</p>
            </div>
          </div>
          
          <div class="feature-item">
            <div class="feature-icon">
              <v-icon color="white" size="24">mdi-chart-line</v-icon>
            </div>
            <div class="feature-text">
              <h3>学习进度跟踪</h3>
              <p>可视化学习成果</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧登录表单 -->
      <div class="login-panel">
        <div class="login-form-container">
          <!-- 表单头部 -->
          <div class="form-header">
            <h2 class="form-title">欢迎回来</h2>
            <p class="form-subtitle">请登录您的账户继续学习之旅</p>
          </div>

          <!-- 登录表单 -->
          <v-form @submit.prevent="onSubmit" class="login-form">
            <!-- 用户名输入 -->
            <div class="input-group">
              <label class="input-label">学/工号</label>
              <div class="input-wrapper">
                <v-text-field
                  v-model="loginForm.username"
                  :rules="usernameRules"
                  variant="outlined"
                  placeholder="请输入学号或工号"
                  prepend-inner-icon="mdi-account"
                  class="modern-input"
                  :class="{ 'input-error': usernameError }"
                  hide-details="auto"
                />
              </div>
            </div>

            <!-- 密码输入 -->
            <div class="input-group">
              <label class="input-label">密码</label>
              <div class="input-wrapper">
                <v-text-field
                  v-model="loginForm.password"
                  :rules="passwordRules"
                  :type="showPassword ? 'text' : 'password'"
                  variant="outlined"
                  placeholder="请输入密码"
                  prepend-inner-icon="mdi-lock"
                  :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                  @click:append-inner="showPassword = !showPassword"
                  class="modern-input"
                  :class="{ 'input-error': passwordError }"
                  hide-details="auto"
                />
              </div>
            </div>

            <!-- 角色选择 -->
            <div class="input-group">
              <label class="input-label">角色</label>
              <div class="role-selector">
                <v-btn-toggle
                  v-model="loginForm.role"
                  mandatory
                  class="role-toggle"
                  color="primary"
                  variant="outlined"
                >
                  <v-btn value="student" class="role-btn">
                    <v-icon left>mdi-school</v-icon>
                    学生
                  </v-btn>
                  <v-btn value="teacher" class="role-btn">
                    <v-icon left>mdi-teach</v-icon>
                    教师
                  </v-btn>
                </v-btn-toggle>
              </div>
            </div>

            <!-- 记住我和忘记密码 -->
            <div class="form-options">
              <v-checkbox
                v-model="rememberMe"
                label="记住我"
                color="primary"
                hide-details
                class="remember-checkbox"
              />
              <a href="#" class="forgot-password">忘记密码？</a>
            </div>

            <!-- 登录按钮 -->
            <v-btn
              type="submit"
              :loading="isLoading"
              class="login-btn modern-btn"
              color="primary"
              size="large"
              block
            >
              <v-icon left>mdi-login</v-icon>
              登录
            </v-btn>

            <!-- 分割线 -->
            <div class="divider">
              <span class="divider-text">或</span>
            </div>

            <!-- 注册按钮 -->
            <v-btn
              @click="goToRegister"
              variant="outlined"
              class="register-btn"
              color="primary"
              size="large"
              block
            >
              <v-icon left>mdi-account-plus</v-icon>
              创建新账户
            </v-btn>
          </v-form>
        </div>
      </div>
    </div>

    <!-- 消息提示 -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
      location="top right"
      class="modern-snackbar"
    >
      <div class="snackbar-content">
        <v-icon left>{{ snackbar.icon }}</v-icon>
        {{ snackbar.text }}
      </div>
    </v-snackbar>

    <!-- 加载覆盖层 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner">
        <v-progress-circular
          indeterminate
          color="primary"
          size="64"
        />
        <p class="loading-text">正在登录...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// 响应式数据
const loginForm = ref({
  username: '',
  password: '',
  role: 'student'
})

const showPassword = ref(false)
const rememberMe = ref(false)
const isLoading = ref(false)
const usernameError = ref(false)
const passwordError = ref(false)

const snackbar = ref({
  show: false,
  text: '',
  color: 'success',
  icon: 'mdi-check-circle'
})

// 验证规则
const usernameRules = [
  v => !!v || '用户名是必需的',
  v => (v && v.length >= 3) || '用户名必须至少3个字符'
]

const passwordRules = [
  v => !!v || '密码是必需的',
  v => (v && v.length >= 5) || '密码必须至少5个字符'
]

// 方法
const showMessage = (text, color = 'success', icon = 'mdi-check-circle') => {
  snackbar.value = {
    show: true,
    text,
    color,
    icon
  }
}

const goToRegister = () => {
  router.push({ name: 'Register' })
}

const validateForm = () => {
  usernameError.value = !loginForm.value.username || loginForm.value.username.length < 3
  passwordError.value = !loginForm.value.password || loginForm.value.password.length < 5
  
  return !usernameError.value && !passwordError.value
}

const onSubmit = async () => {
  if (!validateForm()) {
    showMessage('请检查输入信息', 'error', 'mdi-alert-circle')
    return
  }

  isLoading.value = true

  try {
    // 模拟网络延迟
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const response = await axios.post(`${window.location.origin}/api/login`, loginForm.value)
    
    // 保存登录信息
    localStorage.setItem('token', response.data.token)
    localStorage.setItem('realname', response.data.realname)
    localStorage.setItem('username', loginForm.value.username)
    localStorage.setItem('tag', loginForm.value.role)
    
    if (rememberMe.value) {
      localStorage.setItem('password', loginForm.value.password)
    }

    showMessage('登录成功！', 'success', 'mdi-check-circle')
    
    // 延迟跳转以显示成功消息
    setTimeout(() => {
      router.push({ name: 'StudentArea' }).then(() => {
        window.location.reload()
      })
    }, 1000)

  } catch (error) {
    console.error('登录失败:', error)
    const errorMessage = error.response?.data?.message || '登录失败，请检查用户名和密码'
    showMessage(errorMessage, 'error', 'mdi-alert-circle')
  } finally {
    isLoading.value = false
  }
}

// 组件挂载时的初始化
onMounted(() => {
  // 检查是否有记住的登录信息
  const savedUsername = localStorage.getItem('username')
  const savedPassword = localStorage.getItem('password')
  
  if (savedUsername) {
    loginForm.value.username = savedUsername
    rememberMe.value = true
  }
  
  if (savedPassword) {
    loginForm.value.password = savedPassword
  }

  // 添加页面加载动画
  document.body.style.overflow = 'hidden'
  setTimeout(() => {
    document.body.style.overflow = 'auto'
  }, 500)
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* 背景装饰 */
.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  z-index: 0;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
  backdrop-filter: blur(40px);
  animation: float 8s ease-in-out infinite;
}

.orb-1 {
  width: 300px;
  height: 300px;
  top: -150px;
  left: -150px;
  animation-delay: 0s;
}

.orb-2 {
  width: 200px;
  height: 200px;
  top: 60%;
  right: -100px;
  animation-delay: 3s;
}

.orb-3 {
  width: 400px;
  height: 400px;
  bottom: -200px;
  left: 50%;
  transform: translateX(-50%);
  animation-delay: 6s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  33% { transform: translateY(-30px) rotate(5deg); }
  66% { transform: translateY(15px) rotate(-5deg); }
}

.floating-particles {
  position: absolute;
  width: 100%;
  height: 100%;
  background-image: 
    radial-gradient(circle at 25% 25%, rgba(255, 255, 255, 0.1) 1px, transparent 1px),
    radial-gradient(circle at 75% 75%, rgba(255, 255, 255, 0.08) 1px, transparent 1px);
  background-size: 50px 50px, 30px 30px;
  animation: particles 20s linear infinite;
}

@keyframes particles {
  0% { transform: translateY(0px); }
  100% { transform: translateY(-100px); }
}

/* 主要内容区域 */
.login-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  max-width: 1200px;
  width: 100%;
  min-height: 600px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.25),
    0 0 0 1px rgba(255, 255, 255, 0.2);
  overflow: hidden;
  position: relative;
  z-index: 1;
  margin: 2rem;
}

/* 左侧信息面板 */
.info-panel {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 3rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.info-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
  pointer-events: none;
}

.brand-section {
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
  z-index: 2;
}

.logo-container {
  margin-bottom: 1.5rem;
}

.brand-logo {
  width: 80px;
  height: 80px;
  object-fit: contain;
  /* 移除滤镜以显示原始LOGO */
  /* filter: brightness(0) invert(1); */
}

.brand-title {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  line-height: 1.6;
}

.features-showcase {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  position: relative;
  z-index: 2;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  opacity: 0;
  animation: slideInLeft 0.6s ease-out forwards;
}

.feature-item:nth-child(1) { animation-delay: 0.2s; }
.feature-item:nth-child(2) { animation-delay: 0.4s; }
.feature-item:nth-child(3) { animation-delay: 0.6s; }

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.feature-icon {
  width: 48px;
  height: 48px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.feature-text h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.feature-text p {
  font-size: 0.9rem;
  opacity: 0.8;
  margin: 0;
}

/* 右侧登录面板 */
.login-panel {
  padding: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-form-container {
  width: 100%;
  max-width: 400px;
}

.form-header {
  text-align: center;
  margin-bottom: 2rem;
}

.form-title {
  font-size: 2rem;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 0.5rem;
}

.form-subtitle {
  color: #6b7280;
  font-size: 0.95rem;
  line-height: 1.5;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #374151;
}

.input-wrapper {
  position: relative;
}

.modern-input :deep(.v-field) {
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.modern-input :deep(.v-field:hover) {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modern-input :deep(.v-field--focused) {
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-error :deep(.v-field) {
  border-color: #ef4444;
}

.role-selector {
  width: 100%;
}

.role-toggle {
  width: 100%;
  height: 48px;
  border-radius: 12px;
  overflow: hidden;
}

.role-btn {
  flex: 1;
  height: 100%;
  border-radius: 0;
  text-transform: none;
  font-weight: 500;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0.5rem 0;
}

.remember-checkbox :deep(.v-label) {
  font-size: 0.9rem;
  color: #4b5563;
}

.forgot-password {
  color: #667eea;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  transition: color 0.2s ease;
}

.forgot-password:hover {
  color: #5a67d8;
}

.login-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: white !important;
  border-radius: 12px !important;
  height: 48px !important;
  font-weight: 600 !important;
  text-transform: none !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
  transition: all 0.2s ease !important;
}

.login-btn:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
}

.divider {
  position: relative;
  text-align: center;
  margin: 1rem 0;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #e5e7eb;
}

.divider-text {
  background: white;
  padding: 0 1rem;
  color: #9ca3af;
  font-size: 0.9rem;
}

.register-btn {
  border-radius: 12px !important;
  height: 48px !important;
  font-weight: 500 !important;
  text-transform: none !important;
  border: 2px solid #667eea !important;
}

/* 消息提示样式 */
.modern-snackbar {
  border-radius: 12px;
}

.snackbar-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* 加载覆盖层 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  text-align: center;
  color: white;
}

.loading-text {
  margin-top: 1rem;
  font-size: 1.1rem;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .login-content {
    grid-template-columns: 1fr;
    max-width: 500px;
  }
  
  .info-panel {
    display: none;
  }
}

@media (max-width: 640px) {
  .login-content {
    margin: 1rem;
    border-radius: 16px;
  }
  
  .login-panel {
    padding: 2rem 1.5rem;
  }
  
  .form-title {
    font-size: 1.75rem;
  }
  
  .role-toggle {
    height: 44px;
  }
  
  .login-btn,
  .register-btn {
    height: 44px !important;
  }
}

/* 性能优化 */
.login-container * {
  box-sizing: border-box;
}

.feature-item,
.gradient-orb {
  will-change: transform;
}

/* 无障碍支持 */
.login-btn:focus,
.register-btn:focus,
.modern-input:focus-within {
  outline: 2px solid #667eea;
  outline-offset: 2px;
}

/* 减少动画对于用户偏好设置 */
@media (prefers-reduced-motion: reduce) {
  .gradient-orb,
  .floating-particles,
  .feature-item {
    animation: none;
  }
}
</style>
