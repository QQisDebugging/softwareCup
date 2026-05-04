<template>
  <div class="data-analysis-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-main">
          <h1 class="page-title gradient-text">📊 数据分析中心</h1>
          <p class="page-subtitle">实时监控平台使用情况和学习数据</p>
        </div>
        <div class="header-stats">
          <div class="quick-stat">
            <v-icon color="primary" size="24">mdi-chart-line</v-icon>
            <span class="stat-value">实时数据</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据概览卡片 -->
    <section class="overview-section">
      <h2 class="section-title">📈 数据概览</h2>
      <div class="overview-grid">
        <div class="overview-card">
          <div class="card-icon success">
            <v-icon color="white" size="32">mdi-account-group</v-icon>
          </div>
          <div class="card-content">
            <h3 class="card-title">活跃用户</h3>
            <p class="card-value">1,234</p>
            <p class="card-trend positive">+12% 本周</p>
          </div>
        </div>
        
        <div class="overview-card">
          <div class="card-icon info">
            <v-icon color="white" size="32">mdi-file-document-multiple</v-icon>
          </div>
          <div class="card-content">
            <h3 class="card-title">作业提交</h3>
            <p class="card-value">856</p>
            <p class="card-trend positive">+8% 本周</p>
          </div>
        </div>
        
        <div class="overview-card">
          <div class="card-icon warning">
            <v-icon color="white" size="32">mdi-clock-outline</v-icon>
          </div>
          <div class="card-content">
            <h3 class="card-title">学习时长</h3>
            <p class="card-value">12.5h</p>
            <p class="card-trend positive">+15% 本周</p>
          </div>
        </div>
        
        <div class="overview-card">
          <div class="card-icon error">
            <v-icon color="white" size="32">mdi-trophy</v-icon>
          </div>
          <div class="card-content">
            <h3 class="card-title">完成率</h3>
            <p class="card-value">87.3%</p>
            <p class="card-trend negative">-2% 本周</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 主要图表区域 -->
    <section class="charts-section">
      <div class="charts-grid">
        <!-- 请求数据图表 -->
        <div class="chart-card primary-chart">
          <div class="chart-header">
            <h3 class="chart-title">🔄 平台使用趋势</h3>
            <p class="chart-subtitle">最近15天的用户活动数据</p>
          </div>
          <div class="chart-content">
            <ChartCard />
          </div>
        </div>

        <!-- 班级提交情况 -->
        <div class="chart-card secondary-chart">
          <div class="chart-header">
            <h3 class="chart-title">👥 班级活动统计</h3>
            <p class="chart-subtitle">各班级的学习活动情况</p>
          </div>
          <div class="chart-content">
            <classSubmissions />
          </div>
        </div>
      </div>
    </section>

    <!-- 今日数据面板 -->
    <section class="today-section">
      <h2 class="section-title">📅 今日实时数据</h2>
      <div class="today-grid">
        <div class="today-card">
          <div class="today-header">
            <div class="today-icon contest">
              <v-icon color="white" size="28">mdi-trophy-variant</v-icon>
            </div>
            <div class="today-info">
              <h4 class="today-title">竞赛提交</h4>
              <p class="today-desc">今日竞赛活动数据</p>
            </div>
          </div>
          <div class="today-content">
            <todayContestSubmissions />
          </div>
        </div>

        <div class="today-card">
          <div class="today-header">
            <div class="today-icon activity">
              <v-icon color="white" size="28">mdi-clipboard-check</v-icon>
            </div>
            <div class="today-info">
              <h4 class="today-title">学习任务</h4>
              <p class="today-desc">今日任务完成情况</p>
            </div>
          </div>
          <div class="today-content">
            <TodayActivities />
          </div>
        </div>

        <div class="today-card">
          <div class="today-header">
            <div class="today-icon assignment">
              <v-icon color="white" size="28">mdi-file-document-edit</v-icon>
            </div>
            <div class="today-info">
              <h4 class="today-title">作业提交</h4>
              <p class="today-desc">今日作业提交统计</p>
            </div>
          </div>
          <div class="today-content">
            <todayAssignments />
          </div>
        </div>
      </div>
    </section>

    <!-- 快速操作面板 -->
    <section class="actions-section">
      <h2 class="section-title">⚡ 快速操作</h2>
      <div class="actions-grid">
        <v-card 
          class="action-card"
          @click="$router.push({ name: 'StudentList' })"
          hover
        >
          <v-card-text class="action-content">
            <div class="action-icon">
              <v-icon color="primary" size="40">mdi-account-group</v-icon>
            </div>
            <h4 class="action-title">学生管理</h4>
            <p class="action-desc">查看和管理学生信息</p>
          </v-card-text>
        </v-card>

        <v-card 
          class="action-card"
          @click="$router.push({ name: 'CreateWork' })"
          hover
        >
          <v-card-text class="action-content">
            <div class="action-icon">
              <v-icon color="success" size="40">mdi-plus-circle</v-icon>
            </div>
            <h4 class="action-title">创建实训</h4>
            <p class="action-desc">发布新的实训项目</p>
          </v-card-text>
        </v-card>

        <v-card 
          class="action-card"
          @click="$router.push({ name: 'CreateContest' })"
          hover
        >
          <v-card-text class="action-content">
            <div class="action-icon">
              <v-icon color="warning" size="40">mdi-file-plus</v-icon>
            </div>
            <h4 class="action-title">创建作业</h4>
            <p class="action-desc">布置新的课程作业</p>
          </v-card-text>
        </v-card>

        <v-card 
          class="action-card"
          @click="$router.push({ name: 'CreateActivity' })"
          hover
        >
          <v-card-text class="action-content">
            <div class="action-icon">
              <v-icon color="info" size="40">mdi-plus-circle-outline</v-icon>
            </div>
            <h4 class="action-title">创建任务</h4>
            <p class="action-desc">发布学习任务</p>
          </v-card-text>
        </v-card>
      </div>
    </section>
  </div>
</template>

<script setup>
import ChartCard from '@/components/RequestDataChart.vue';
import todayContestSubmissions from '@/components/todayContestSubmissions.vue';
import TodayActivities from '@/components/TodayActivities.vue';
import todayAssignments from '@/components/todayAssignments.vue';
import classSubmissions from '@/components/classSubmissions.vue';
</script>

<style scoped>
.data-analysis-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem;
}

/* 页面头部 */
.page-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.header-main h1.page-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.gradient-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 1.1rem;
  color: #666;
  margin: 0;
}

.header-stats {
  display: flex;
  gap: 1rem;
}

.quick-stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(102, 126, 234, 0.1);
  padding: 0.75rem 1rem;
  border-radius: 12px;
}

.stat-value {
  font-weight: 600;
  color: #667eea;
}

/* 数据概览section */
.overview-section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1rem;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.overview-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-icon.success { background: linear-gradient(135deg, #4CAF50, #45a049); }
.card-icon.info { background: linear-gradient(135deg, #2196F3, #1976D2); }
.card-icon.warning { background: linear-gradient(135deg, #FF9800, #F57C00); }
.card-icon.error { background: linear-gradient(135deg, #F44336, #D32F2F); }

.card-content {
  flex: 1;
}

.card-title {
  font-size: 0.9rem;
  color: #666;
  margin: 0 0 0.25rem 0;
}

.card-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #333;
  margin: 0 0 0.25rem 0;
}

.card-trend {
  font-size: 0.8rem;
  font-weight: 600;
  margin: 0;
}

.card-trend.positive { color: #4CAF50; }
.card-trend.negative { color: #F44336; }

/* 图表区域 */
.charts-section {
  margin-bottom: 2rem;
}

.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}

.chart-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chart-header {
  padding: 1.5rem 1.5rem 0;
}

.chart-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.25rem 0;
}

.chart-subtitle {
  font-size: 0.9rem;
  color: #666;
  margin: 0;
}

.chart-content {
  padding: 1rem 1.5rem 1.5rem;
}

/* 今日数据section */
.today-section {
  margin-bottom: 2rem;
}

.today-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.today-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
}

.today-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(0, 0, 0, 0.15);
}

.today-header {
  padding: 1.5rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.today-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.today-icon.contest { background: linear-gradient(135deg, #667eea, #764ba2); }
.today-icon.activity { background: linear-gradient(135deg, #4CAF50, #45a049); }
.today-icon.assignment { background: linear-gradient(135deg, #FF9800, #F57C00); }

.today-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.25rem 0;
}

.today-desc {
  font-size: 0.85rem;
  color: #666;
  margin: 0;
}

.today-content {
  padding: 1.5rem;
}

/* 快速操作section */
.actions-section {
  margin-bottom: 2rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.action-card {
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.action-content {
  text-align: center;
  padding: 2rem 1.5rem;
}

.action-icon {
  margin-bottom: 1rem;
}

.action-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.5rem 0;
}

.action-desc {
  font-size: 0.9rem;
  color: #666;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .data-analysis-container {
    padding: 1rem;
  }
  
  .header-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .overview-grid {
    grid-template-columns: 1fr;
  }
  
  .today-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .actions-grid {
    grid-template-columns: 1fr;
  }
  
  .header-main h1.page-title {
    font-size: 2rem;
  }
}

/* 动画效果 */
.overview-card,
.chart-card,
.today-card,
.action-card {
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
  