<template>
  <div class="student-area-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-main">
          <div class="title-wrapper">
            <div class="title-decoration">
              <div class="decoration-line"></div>
              <v-icon class="title-icon" color="white" size="40">mdi-school</v-icon>
              <div class="decoration-line"></div>
            </div>
            <h1 class="page-title gradient-text">学生工具中心</h1>
            <p class="page-subtitle">探索强大的AI工具，提升学习效率</p>
            <div class="subtitle-stats">
              <div class="stat-pill">
                <v-icon size="16">mdi-tools</v-icon>
                <span>{{ tools.length }} 个工具</span>
              </div>
              <div class="stat-pill">
                <v-icon size="16">mdi-trending-up</v-icon>
                <span>持续更新</span>
              </div>
            </div>
          </div>
        </div>
        <div class="header-decoration">
          <div class="floating-elements">
            <div class="element element-1">
              <v-icon color="white" size="24">mdi-brain</v-icon>
            </div>
            <div class="element element-2">
              <v-icon color="white" size="20">mdi-code-tags</v-icon>
            </div>
            <div class="element element-3">
              <v-icon color="white" size="18">mdi-rocket</v-icon>
            </div>
            <div class="element element-4">
              <v-icon color="white" size="22">mdi-lightbulb</v-icon>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 特色功能卡片 -->
    <section class="featured-section">
      <div class="section-header">
        <div class="section-title-wrapper">
          <div class="section-icon">
            <v-icon color="warning" size="32">mdi-star</v-icon>
          </div>
          <div class="section-title-content">
            <h2 class="section-title">今日推荐</h2>
            <p class="section-subtitle">每日精选功能，助力高效学习</p>
          </div>
        </div>
      </div>
      
      <div class="featured-grid">
        <ModernCard
          :title="dailyFeature.title"
          :description="dailyFeature.description"
          :imageSrc="dailyFeature.image"
          :icon="dailyFeature.icon"
          :featured="true"
          :badge="dailyFeature.badge"
          :to="dailyFeature.route"
          @click="navigateToRoute"
          class="featured-card bounce-in enhanced-card"
        />
      </div>
    </section>

    <!-- 工具网格 -->
    <section class="tools-section">
      <div class="section-header">
        <div class="section-title-wrapper">
          <div class="section-icon">
            <v-icon color="primary" size="32">mdi-toolbox</v-icon>
          </div>
          <div class="section-title-content">
            <h2 class="section-title">智能工具</h2>
            <p class="section-subtitle">专为学习打造的AI工具集合</p>
          </div>
        </div>
      </div>

      <!-- 工具过滤器 -->
      <div class="tools-filter" data-aos="fade-up">
        <v-chip-group v-model="selectedCategory" color="primary" class="filter-chips">
          <v-chip value="all" variant="elevated">
            <v-icon left size="16">mdi-view-grid</v-icon>
            全部工具
          </v-chip>
          <v-chip value="ai" variant="elevated">
            <v-icon left size="16">mdi-brain</v-icon>
            AI工具
          </v-chip>
          <v-chip value="code" variant="elevated">
            <v-icon left size="16">mdi-code-tags</v-icon>
            代码工具
          </v-chip>
          <v-chip value="analysis" variant="elevated">
            <v-icon left size="16">mdi-chart-line</v-icon>
            分析工具
          </v-chip>
        </v-chip-group>
      </div>

      <div class="tools-grid">
        <ModernCard
          v-for="(tool, index) in filteredTools"
          :key="tool.id"
          :title="tool.title"
          :description="tool.description"
          :imageSrc="tool.image"
          :icon="tool.icon"
          :tags="tool.tags"
          :progress="tool.progress"
          :badge="tool.badge"
          :to="tool.route"
          @click="navigateToRoute"
          :class="`tool-card fade-in-up enhanced-card`"
          :style="{ 'animation-delay': `${index * 100}ms` }"
        />
      </div>
    </section>

    <!-- 统计信息卡片 -->
    <section class="stats-section">
      <div class="section-header">
        <div class="section-title-wrapper">
          <div class="section-icon">
            <v-icon color="success" size="32">mdi-chart-donut</v-icon>
          </div>
          <div class="section-title-content">
            <h2 class="section-title">学习统计</h2>
            <p class="section-subtitle">追踪你的学习进度</p>
          </div>
        </div>
      </div>
      
      <div class="stats-grid">
        <div 
          v-for="(stat, index) in stats" 
          :key="stat.label"
          class="stat-card floating-card enhanced-stat-card"
          :class="`bounce-in`"
          :style="{ 'animation-delay': `${index * 150}ms` }"
          @click="handleStatClick(stat)"
        >
          <div class="stat-background"></div>
          <div class="stat-icon">
            <div class="icon-wrapper">
              <v-icon :color="stat.color" size="32">{{ stat.icon }}</v-icon>
            </div>
          </div>
          <div class="stat-content">
            <div class="stat-value" :style="{ color: `var(--v-theme-${stat.color})` }">
              <span class="animated-number">{{ stat.value }}</span>
            </div>
            <div class="stat-label">{{ stat.label }}</div>
            <div class="stat-trend">
              <v-icon size="14" color="success">mdi-trending-up</v-icon>
              <span class="trend-text">+{{ (index + 1) * 12 }}%</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 快速访问栏 -->
    <section class="quick-access-section">
      <div class="quick-access-container">
        <div class="quick-access-header">
          <h3 class="quick-access-title">
            <v-icon color="primary" size="24">mdi-lightning-bolt</v-icon>
            快速访问
          </h3>
          <p class="quick-access-subtitle">一键直达常用功能</p>
        </div>
        <div class="quick-access-buttons">
          <v-btn
            v-for="(quick, index) in quickAccess"
            :key="quick.name"
            :color="quick.color"
            variant="elevated"
            class="quick-btn modern-btn enhanced-quick-btn"
            @click="navigateTo(quick.route)"
            :style="{ 'animation-delay': `${index * 100}ms` }"
          >
            <v-icon left>{{ quick.icon }}</v-icon>
            {{ quick.name }}
            <div class="btn-shine"></div>
          </v-btn>
        </div>
      </div>
    </section>

    <!-- 最近活动时间线 -->
    <section class="timeline-section">
      <div class="section-header">
        <div class="section-title-wrapper">
          <div class="section-icon">
            <v-icon color="info" size="32">mdi-timeline</v-icon>
          </div>
          <div class="section-title-content">
            <h2 class="section-title">最近活动</h2>
            <p class="section-subtitle">查看你的学习轨迹</p>
          </div>
        </div>
      </div>
      
      <div class="timeline-container">
        <div class="timeline-item" v-for="(activity, index) in recentActivities" :key="index">
          <div class="timeline-icon">
            <v-icon :color="activity.color" size="20">{{ activity.icon }}</v-icon>
          </div>
          <div class="timeline-content">
            <h4 class="timeline-title">{{ activity.title }}</h4>
            <p class="timeline-description">{{ activity.description }}</p>
            <span class="timeline-time">{{ activity.time }}</span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import ModernCard from '@/components/ModernCard.vue'
import { addRequests } from '@/utils/commonUtil'

const router = useRouter()

// 选中的工具分类
const selectedCategory = ref('all')

// 每日推荐功能
const dailyFeature = ref({
  title: '每日一测',
  description: '每天挑战新题目，持续提升编程能力。今日题目：算法优化专题',
  image: '/src/assets/8.jpg',
  icon: 'mdi-brain',
  badge: '今日推荐',
  route: 'DailyTest'
})

// 工具列表数据
const tools = ref([
  {
    id: 1,
    title: '代码助手',
    description: 'AI驱动的代码智能分析和建议工具，帮助你写出更优质的代码',
    image: '/src/assets/1.jpg',
    icon: 'mdi-code-tags',
    tags: ['AI', '代码分析', '智能提示'],
    route: 'CodeHelper',
    progress: 85,
    category: 'ai'
  },
  {
    id: 2,
    title: '拍照答题',
    description: '上传题目图片，AI快速识别并提供详细解答步骤',
    image: '/src/assets/3.jpg',
    icon: 'mdi-camera',
    tags: ['图像识别', '智能解答', 'OCR'],
    route: 'ImageProblemSolve',
    badge: 'AI驱动',
    category: 'ai'
  },
  {
    id: 3,
    title: '代码纠错',
    description: '智能检测代码错误，提供修复建议和最佳实践指导',
    image: '/src/assets/4.jpg',
    icon: 'mdi-bug',
    tags: ['错误检测', '代码质量', '优化建议'],
    route: 'CodeCorrect',
    progress: 92,
    category: 'code'
  },
  {
    id: 4,
    title: '代码解析',
    description: '深度解析代码逻辑，生成可视化流程图和详细注释',
    image: '/src/assets/2.png',
    icon: 'mdi-file-tree',
    tags: ['代码分析', '可视化', '注释生成'],
    route: 'CodeAnalysis',
    category: 'analysis'
  },
  {
    id: 5,
    title: 'SQL语句生成',
    description: '根据自然语言描述，智能生成高效的SQL查询语句',
    image: '/src/assets/8.jpg',
    icon: 'mdi-database',
    tags: ['SQL', '自然语言', '数据查询'],
    route: 'SqlGenerate',
    badge: '新功能',
    category: 'ai'
  },
  {
    id: 6,
    title: '流程图生成',
    description: '从代码自动生成清晰的流程图，帮助理解程序逻辑',
    image: '/src/assets/7.jpg',
    icon: 'mdi-sitemap',
    tags: ['流程图', '可视化', '逻辑图'],
    route: 'FlowChartGenerate',
    category: 'analysis'
  },
  {
    id: 7,
    title: '程序设计园地',
    description: '编程学习资源中心，包含教程、实例和练习题库',
    image: '/src/assets/3.jpg',
    icon: 'mdi-school',
    tags: ['学习资源', '教程', '练习'],
    route: 'CodeBasicSkill',
    progress: 78,
    category: 'code'
  }
])

// 统计数据
const stats = ref([
  {
    label: '工具使用次数',
    value: '248',
    icon: 'mdi-chart-line',
    color: 'primary'
  },
  {
    label: '解决问题数',
    value: '156',
    icon: 'mdi-check-circle',
    color: 'success'
  },
  {
    label: '学习时长',
    value: '32h',
    icon: 'mdi-clock',
    color: 'warning'
  },
  {
    label: '代码行数',
    value: '15.2k',
    icon: 'mdi-code-braces',
    color: 'info'
  }
])

// 快速访问按钮
const quickAccess = ref([
  { name: '我的主页', icon: 'mdi-home', route: 'StudentAccount', color: 'primary' },
  { name: '我的作业', icon: 'mdi-clipboard-text', route: 'GetStudetContest', color: 'secondary' },
  { name: '学习排行', icon: 'mdi-trophy', route: 'StudyRank', color: 'success' },
  { name: '实训任务', icon: 'mdi-code-tags', route: 'GetStudetWork', color: 'warning' }
])

// 最近活动数据
const recentActivities = ref([
  {
    title: '完成代码助手分析',
    description: '使用AI助手成功分析了Python项目代码',
    time: '2小时前',
    icon: 'mdi-check-circle',
    color: 'success'
  },
  {
    title: '使用拍照答题功能',
    description: '上传数学题目并获得详细解答',
    time: '4小时前',
    icon: 'mdi-camera',
    color: 'primary'
  },
  {
    title: '生成SQL查询语句',
    description: '通过自然语言描述生成复杂查询',
    time: '昨天',
    icon: 'mdi-database',
    color: 'info'
  }
])

// 计算属性：过滤工具
const filteredTools = computed(() => {
  if (selectedCategory.value === 'all') {
    return tools.value
  }
  return tools.value.filter(tool => tool.category === selectedCategory.value)
})

// 方法
const navigateTo = (route) => {
  if (route) {
    router.push({ name: route })
  }
}

const navigateToRoute = (route) => {
  navigateTo(route)
}

const handleStatClick = (stat) => {
  // 可以添加统计详情查看功能
  console.log('查看统计详情:', stat)
}

onMounted(() => {
  addRequests()
  // 添加页面加载动画
  document.body.style.overflow = 'hidden'
  setTimeout(() => {
    document.body.style.overflow = 'auto'
  }, 1000)
})
</script>

<style scoped>
.student-area-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-attachment: fixed;
  position: relative;
  overflow-x: hidden;
}

.student-area-container::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
    radial-gradient(circle at 40% 80%, rgba(120, 219, 226, 0.3) 0%, transparent 50%);
  pointer-events: none;
  z-index: -1;
}

/* 页面头部增强 */
.page-header {
  padding: 4rem 2rem 2rem;
  text-align: center;
  position: relative;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
}

.title-wrapper {
  margin-bottom: 2rem;
}

.title-decoration {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.decoration-line {
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.6) 50%, transparent 100%);
}

.title-icon {
  animation: iconGlow 3s ease-in-out infinite alternate;
}

@keyframes iconGlow {
  0% { filter: drop-shadow(0 0 5px rgba(255, 255, 255, 0.5)); }
  100% { filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.8)); }
}

.page-title {
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 800;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.page-subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.9);
  max-width: 600px;
  margin: 0 auto 1.5rem;
  line-height: 1.6;
}

.subtitle-stats {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.stat-pill {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 0.9rem;
  font-weight: 500;
}

.floating-elements {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.element {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: float 6s ease-in-out infinite;
  display: flex;
  align-items: center;
  justify-content: center;
}

.element-1 {
  width: 80px;
  height: 80px;
  top: 20%;
  left: 10%;
  animation-delay: 0s;
}

.element-2 {
  width: 60px;
  height: 60px;
  top: 60%;
  right: 10%;
  animation-delay: 2s;
}

.element-3 {
  width: 50px;
  height: 50px;
  top: 10%;
  right: 30%;
  animation-delay: 4s;
}

.element-4 {
  width: 70px;
  height: 70px;
  bottom: 20%;
  left: 15%;
  animation-delay: 6s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(180deg); }
}

/* 章节通用样式增强 */
.featured-section,
.tools-section,
.stats-section,
.quick-access-section,
.timeline-section {
  padding: 3rem 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 3rem;
}

.section-title-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.section-icon {
  padding: 1rem;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(20px);
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.section-title-content {
  text-align: left;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin: 0 0 0.5rem 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section-subtitle {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

/* 工具过滤器 */
.tools-filter {
  margin-bottom: 3rem;
  display: flex;
  justify-content: center;
}

.filter-chips {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 2rem;
  padding: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 特色功能区域 */
.featured-grid {
  display: grid;
  max-width: 600px;
  margin: 0 auto;
}

.featured-card {
  transform: scale(1.05);
}

/* 工具网格 */
.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.tool-card {
  opacity: 0;
  transform: translateY(30px);
  animation-fill-mode: forwards;
}

/* 增强卡片效果 */
.enhanced-card {
  position: relative;
  overflow: hidden;
}

.enhanced-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.5s ease;
  z-index: 1;
}

.enhanced-card:hover::before {
  left: 100%;
}

/* 统计卡片增强 */
.stats-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 2rem;
  margin: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.enhanced-stat-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 1.5rem;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

.enhanced-stat-card:hover {
  transform: translateY(-8px) scale(1.02) rotateX(5deg);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.stat-background {
  position: absolute;
  top: 0;
  right: 0;
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  transform: translate(30px, -30px);
}

.icon-wrapper {
  padding: 1rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  display: inline-flex;
  margin-bottom: 1rem;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
  position: relative;
}

.animated-number {
  display: inline-block;
  animation: numberPulse 2s ease-in-out infinite;
}

@keyframes numberPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.stat-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: #4a5568;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.5rem;
}

.stat-trend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  opacity: 0.8;
}

.trend-text {
  font-size: 0.8rem;
  font-weight: 600;
  color: #10b981;
}

/* 快速访问区域增强 */
.quick-access-section {
  background: rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(20px);
  border-radius: 2rem;
  margin: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.quick-access-container {
  text-align: center;
}

.quick-access-header {
  margin-bottom: 2rem;
}

.quick-access-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.quick-access-subtitle {
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.quick-access-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
  align-items: center;
}

.enhanced-quick-btn {
  background: rgba(255, 255, 255, 0.1) !important;
  color: white !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  backdrop-filter: blur(10px) !important;
  border-radius: 2rem !important;
  padding: 0.75rem 1.5rem !important;
  font-weight: 500 !important;
  text-transform: none !important;
  transition: all 0.3s ease !important;
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.6s ease-out forwards;
  opacity: 0;
  transform: translateY(20px);
}

.enhanced-quick-btn:hover {
  background: rgba(255, 255, 255, 0.2) !important;
  transform: translateY(-2px) scale(1.05) !important;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
}

.btn-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.enhanced-quick-btn:hover .btn-shine {
  left: 100%;
}

/* 时间线部分 */
.timeline-section {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 2rem;
  margin: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.timeline-container {
  max-width: 600px;
  margin: 0 auto;
  position: relative;
}

.timeline-container::before {
  content: '';
  position: absolute;
  left: 20px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0.3), transparent);
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 2rem;
  position: relative;
}

.timeline-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  z-index: 2;
}

.timeline-content {
  flex: 1;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 1rem;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.timeline-title {
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
}

.timeline-description {
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 0.5rem 0;
  line-height: 1.5;
}

.timeline-time {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    padding: 2rem 1rem 1rem;
  }
  
  .tools-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
  
  .quick-access-buttons {
    flex-direction: column;
    align-items: stretch;
  }
  
  .enhanced-quick-btn {
    width: 100%;
    max-width: 300px;
    margin: 0 auto;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .section-title-wrapper {
    flex-direction: column;
    text-align: center;
  }
  
  .section-title-content {
    text-align: center;
  }
  
  .featured-section,
  .tools-section,
  .stats-section,
  .quick-access-section,
  .timeline-section {
    padding: 2rem 1rem;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .enhanced-stat-card {
    padding: 1.5rem;
  }
  
  .stat-value {
    font-size: 2rem;
  }
  
  .subtitle-stats {
    flex-direction: column;
    align-items: center;
  }
}

/* 动画增强 */
.fade-in-up {
  opacity: 0;
  transform: translateY(30px);
  animation: fadeInUp 0.6s ease-out forwards;
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.bounce-in {
  opacity: 0;
  transform: scale(0.8);
  animation: bounceIn 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards;
}

@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.8);
  }
  50% {
    opacity: 0.9;
    transform: scale(1.05);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

/* 滚动优化 */
.student-area-container {
  scroll-behavior: smooth;
}

/* 性能优化：减少重绘 */
.tool-card,
.enhanced-stat-card,
.enhanced-quick-btn {
  will-change: transform;
}

.tool-card:hover,
.enhanced-stat-card:hover,
.enhanced-quick-btn:hover {
  will-change: auto;
}
</style>
