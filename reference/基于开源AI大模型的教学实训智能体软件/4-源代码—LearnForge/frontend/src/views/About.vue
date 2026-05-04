<template>
  <div class="about-container">
    <!-- 页面背景装饰 -->
    <div class="background-decoration">
      <div class="floating-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
      </div>
    </div>

    <!-- 主要内容 -->
    <v-container class="main-content">
      <v-row justify="center" align="center" class="min-height-screen">
        <v-col cols="12" md="10" lg="8">
          <!-- Logo和标题区域 -->
          <div class="hero-section" data-aos="fade-up">
            <div class="logo-container">
              <div class="logo-wrapper">
                <img 
                  src="@/assets/logo/logo.png" 
                  alt="LearnForge Logo" 
                  class="main-logo"
                />
                <div class="logo-glow"></div>
              </div>
            </div>
            
            <div class="title-section">
              <h1 class="main-title gradient-text">LearnForge</h1>
              <div class="subtitle-container">
                <v-icon class="subtitle-icon" color="primary">mdi-school</v-icon>
                <span class="subtitle">AI赋能教育，智创未来</span>
              </div>
              <p class="description">
                基于人工智能技术的现代化教育平台，为学习者提供智能化、个性化的学习体验
              </p>
            </div>
          </div>

          <!-- 特色功能展示 -->
          <div class="features-section" data-aos="fade-up" data-aos-delay="200">
            <div class="features-grid">
              <div class="feature-card" data-aos="zoom-in" data-aos-delay="300">
                <v-icon class="feature-icon" color="primary">mdi-brain</v-icon>
                <h3>AI智能助手</h3>
                <p>先进的AI技术提供个性化学习指导</p>
              </div>
              <div class="feature-card" data-aos="zoom-in" data-aos-delay="400">
                <v-icon class="feature-icon" color="secondary">mdi-code-tags</v-icon>
                <h3>编程工具</h3>
                <p>专业的代码分析与优化工具集</p>
              </div>
              <div class="feature-card" data-aos="zoom-in" data-aos-delay="500">
                <v-icon class="feature-icon" color="success">mdi-chart-line</v-icon>
                <h3>学习分析</h3>
                <p>数据驱动的学习进度追踪</p>
              </div>
            </div>
          </div>

          <!-- 团队信息 -->
          <div class="team-section" data-aos="fade-up" data-aos-delay="600">
            <v-card class="team-card glass-card">
              <v-card-text class="team-content">
                <div class="team-header">
                  <v-icon class="team-icon" color="primary" size="32">mdi-account-group</v-icon>
                  <h3 class="team-title">开发团队</h3>
                </div>
                
                <div class="team-members">
                  <div class="member-card" v-for="member in teamMembers" :key="member.name">
                    <v-avatar class="member-avatar" :color="member.color" size="48">
                      <span class="member-initial">{{ member.name.charAt(0) }}</span>
                    </v-avatar>
                    <div class="member-info">
                      <p class="member-name">{{ member.name }}</p>
                      <p class="member-role">{{ member.role }}</p>
                    </div>
                  </div>
                </div>

                <v-divider class="my-4"></v-divider>

                <div class="supervisor-section">
                  <v-icon class="supervisor-icon" color="warning">mdi-account-star</v-icon>
                  <div class="supervisor-info">
                    <span class="supervisor-label">指导教师</span>
                    <span class="supervisor-name">谢昭</span>
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </div>

          <!-- 版权信息 -->
          <div class="copyright-section" data-aos="fade-up" data-aos-delay="800">
            <div class="copyright-card">
              <v-icon class="copyright-icon">mdi-copyright</v-icon>
              <span class="copyright-text">
                Copyright © LearnForge 2025 XiaoningYu. All rights reserved.
              </span>
            </div>
          </div>

          <!-- 开始使用按钮 -->
          <div class="action-section" data-aos="fade-up" data-aos-delay="900">
            <v-btn
              class="start-btn"
              color="primary"
              size="x-large"
              rounded="xl"
              elevation="8"
              @click="navigateToLogin"
            >
              <v-icon left>mdi-rocket-launch</v-icon>
              开始探索
            </v-btn>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { addRequests } from '@/utils/commonUtil'

const router = useRouter()

// 团队成员数据
const teamMembers = ref([
  { name: '于晓宁', role: '项目负责人', color: 'primary' },
  { name: '姚心雨', role: '前端开发', color: 'secondary' },
  { name: '卢思颖', role: '后端开发', color: 'success' }
])

// 导航到登录页面
const navigateToLogin = () => {
  router.push({ name: 'Login' })
}

onMounted(() => {
  addRequests()
  
  // 初始化AOS动画库（如果有的话）
  if (typeof AOS !== 'undefined') {
    AOS.init({
      duration: 800,
      easing: 'ease-in-out',
      once: true
    })
  }
})
</script>

<style scoped>
.about-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-attachment: fixed;
  position: relative;
  overflow-x: hidden;
}

/* 背景装饰 */
.background-decoration {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
}

.floating-shapes {
  position: relative;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 8s ease-in-out infinite;
}

.shape-1 {
  width: 100px;
  height: 100px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.shape-2 {
  width: 150px;
  height: 150px;
  top: 20%;
  right: 15%;
  animation-delay: 2s;
}

.shape-3 {
  width: 80px;
  height: 80px;
  bottom: 30%;
  left: 20%;
  animation-delay: 4s;
}

.shape-4 {
  width: 120px;
  height: 120px;
  bottom: 20%;
  right: 10%;
  animation-delay: 6s;
}

@keyframes float {
  0%, 100% { 
    transform: translateY(0px) rotate(0deg); 
    opacity: 0.7;
  }
  50% { 
    transform: translateY(-30px) rotate(180deg); 
    opacity: 1;
  }
}

/* 主要内容 */
.main-content {
  position: relative;
  z-index: 1;
  padding: 2rem 0;
}

.min-height-screen {
  min-height: 100vh;
}

/* Hero区域 */
.hero-section {
  text-align: center;
  margin-bottom: 4rem;
}

.logo-container {
  margin-bottom: 2rem;
}

.logo-wrapper {
  position: relative;
  display: inline-block;
}

.main-logo {
  width: 200px;
  height: 200px;
  object-fit: contain;
  border-radius: 50%;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  animation: logoFloat 4s ease-in-out infinite;
  position: relative;
  z-index: 2;
}

.logo-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 220px;
  height: 220px;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.3) 0%, transparent 70%);
  border-radius: 50%;
  animation: pulse 3s ease-in-out infinite;
  z-index: 1;
}

@keyframes logoFloat {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

@keyframes pulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.7; }
  50% { transform: translate(-50%, -50%) scale(1.1); opacity: 1; }
}

.title-section {
  margin-bottom: 3rem;
}

.main-title {
  font-size: clamp(3rem, 8vw, 5rem);
  font-weight: 800;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 50%, #e0f2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  animation: titleGlow 3s ease-in-out infinite alternate;
}

@keyframes titleGlow {
  0% { filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5)); }
  100% { filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.8)); }
}

.subtitle-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.subtitle-icon {
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-5px); }
  60% { transform: translateY(-3px); }
}

.subtitle {
  font-size: 1.5rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.description {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* 特色功能 */
.features-section {
  margin-bottom: 4rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  max-width: 900px;
  margin: 0 auto;
}

.feature-card {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(20px);
  border-radius: 2rem;
  padding: 2rem;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  cursor: pointer;
}

.feature-card:hover {
  transform: translateY(-10px) scale(1.02);
  background: rgba(255, 255, 255, 0.25);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.feature-icon {
  font-size: 3rem !important;
  margin-bottom: 1rem;
  animation: iconPulse 3s ease-in-out infinite;
}

@keyframes iconPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.feature-card h3 {
  font-size: 1.3rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.5rem;
}

.feature-card p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  line-height: 1.5;
}

/* 团队信息 */
.team-section {
  margin-bottom: 4rem;
}

.team-card {
  max-width: 600px;
  margin: 0 auto;
}

.glass-card {
  background: rgba(255, 255, 255, 0.15) !important;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 2rem !important;
}

.team-content {
  padding: 2.5rem !important;
}

.team-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.team-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: white;
  margin: 0;
}

.team-members {
  display: grid;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.member-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  transition: all 0.3s ease;
}

.member-card:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(10px);
}

.member-avatar {
  flex-shrink: 0;
}

.member-initial {
  font-weight: 600;
  color: white;
}

.member-info {
  flex: 1;
}

.member-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: white;
  margin: 0 0 0.25rem 0;
}

.member-role {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

.supervisor-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.supervisor-info {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.supervisor-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
}

.supervisor-name {
  font-size: 1.2rem;
  font-weight: 600;
  color: white;
}

/* 版权信息 */
.copyright-section {
  margin-bottom: 3rem;
}

.copyright-card {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  max-width: 500px;
  margin: 0 auto;
}

.copyright-icon {
  color: rgba(255, 255, 255, 0.7);
}

.copyright-text {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
}

/* 操作按钮 */
.action-section {
  text-align: center;
}

.start-btn {
  font-size: 1.1rem !important;
  font-weight: 600 !important;
  padding: 1rem 3rem !important;
  text-transform: none !important;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: white !important;
  border: none !important;
  animation: buttonGlow 3s ease-in-out infinite alternate;
  transition: all 0.3s ease !important;
}

.start-btn:hover {
  transform: translateY(-3px) scale(1.05) !important;
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3) !important;
}

@keyframes buttonGlow {
  0% { box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4); }
  100% { box-shadow: 0 8px 25px rgba(118, 75, 162, 0.6); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-logo {
    width: 150px;
    height: 150px;
  }
  
  .logo-glow {
    width: 170px;
    height: 170px;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .team-content {
    padding: 1.5rem !important;
  }
  
  .member-card {
    flex-direction: column;
    text-align: center;
  }
  
  .start-btn {
    width: 100%;
    max-width: 300px;
  }
}

@media (max-width: 480px) {
  .shape {
    display: none;
  }
  
  .feature-card {
    padding: 1.5rem;
  }
  
  .copyright-card {
    flex-direction: column;
    gap: 0.5rem;
    padding: 1rem;
  }
}

/* 性能优化 */
.feature-card,
.member-card,
.start-btn {
  will-change: transform;
}

.feature-card:hover,
.member-card:hover,
.start-btn:hover {
  will-change: auto;
}
</style>