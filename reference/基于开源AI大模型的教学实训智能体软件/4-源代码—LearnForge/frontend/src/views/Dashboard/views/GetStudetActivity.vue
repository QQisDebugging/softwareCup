<template>
  <div class="activity-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-main">
          <div class="title-wrapper">
            <div class="title-decoration">
              <div class="decoration-line"></div>
              <v-icon class="title-icon" color="white" size="40">mdi-clipboard-check</v-icon>
              <div class="decoration-line"></div>
            </div>
            <h1 class="page-title gradient-text">我的任务</h1>
            <p class="page-subtitle">完成学习任务，提升综合能力</p>
          </div>
        </div>
        <div class="header-decoration">
          <div class="floating-elements">
            <div class="element element-1">
              <v-icon color="white" size="24">mdi-lightbulb</v-icon>
            </div>
            <div class="element element-2">
              <v-icon color="white" size="20">mdi-target</v-icon>
            </div>
            <div class="element element-3">
              <v-icon color="white" size="18">mdi-star</v-icon>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <v-container class="activity-content">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <v-progress-circular
            indeterminate
            color="primary"
            size="64"
          ></v-progress-circular>
          <p class="loading-text">正在加载任务数据...</p>
        </div>

        <!-- 空状态 -->
        <div v-else-if="!activities.length" class="empty-state">
          <div class="empty-icon">
            <v-icon size="80" color="grey-lighten-2">mdi-clipboard-outline</v-icon>
          </div>
          <h3 class="empty-title">暂无学习任务</h3>
          <p class="empty-subtitle">老师还没有发布学习任务，请稍后再来查看</p>
        </div>

        <!-- 任务列表 -->
        <div v-else class="activity-grid">
          <div 
            v-for="(activity, index) in activities" 
            :key="activity.activity_id"
            class="activity-item"
            :style="{ animationDelay: `${index * 0.1}s` }"
          >
            <v-card
              class="activity-card"
              elevation="0"
              @click="goToDetail(activity.activity_id)"
            >
              <div class="card-header">
                <div class="card-icon">
                  <v-icon color="white" size="32">mdi-book-open</v-icon>
                </div>
                <div class="card-meta">
                  <v-chip
                    size="small"
                    color="secondary"
                    variant="tonal"
                    class="activity-id-chip"
                  >
                    任务 #{{ activity.activity_id }}
                  </v-chip>
                </div>
              </div>

              <div class="card-content">
                <h3 class="activity-title">{{ activity.activity_name }}</h3>
                
                <div class="activity-details">
                  <div class="detail-item">
                    <v-icon size="16" color="grey-darken-1">mdi-calendar-plus</v-icon>
                    <span>{{ formattedSubmissionDate(activity.created_date) }}</span>
                  </div>
                  <div class="detail-item">
                    <v-icon size="16" color="grey-darken-1">mdi-clock-outline</v-icon>
                    <span>{{ activity.estimated_time || '预计 2 小时' }}</span>
                  </div>
                </div>

                <div class="description-section">
                  <div class="description-preview">
                    <v-md-preview 
                      :text="activity.description" 
                      class="md-preview-container"
                    />
                  </div>
                </div>

                <div class="priority-section">
                  <v-chip
                    :color="getPriorityColor(activity.priority)"
                    variant="flat"
                    size="small"
                    class="priority-chip"
                  >
                    <v-icon size="14" start>mdi-flag</v-icon>
                    {{ getPriorityText(activity.priority) }}
                  </v-chip>
                </div>
              </div>

              <div class="card-actions">
                <v-btn
                  variant="outlined"
                  color="secondary"
                  size="small"
                  @click.stop="goToDetail(activity.activity_id)"
                  class="action-btn"
                >
                  <v-icon size="16" start>mdi-eye</v-icon>
                  查看详情
                </v-btn>
                <v-btn
                  color="secondary"
                  size="small"
                  @click.stop="goToSubmit(activity.activity_id)"
                  class="action-btn primary-btn"
                >
                  <v-icon size="16" start>mdi-rocket-launch</v-icon>
                  开始任务
                </v-btn>
              </div>

              <div class="card-hover-overlay">
                <v-icon size="24" color="white">mdi-arrow-right</v-icon>
              </div>
            </v-card>
          </div>
        </div>
      </v-container>
    </div>
  </div>
</template>

<script>
import axios from '@/utils/axiosConfig';
import moment from 'moment';

export default {
  name: 'GetStudentActivity',
  data() {
    return {
      activities: [],
      loading: true,
      sno: localStorage.getItem('username'),
    };
  },
  mounted() {
    this.fetchStudentActivities();
  },
  methods: {
    formattedSubmissionDate(submissionDate) {
      return moment(submissionDate).format('YYYY-MM-DD HH:mm');
    },
    async fetchStudentActivities() {
      this.loading = true;
      try {
        const response = await axios.get(`${this.$backendUrl}/api/getStudentActivities`, {
          params: { sno: this.sno }
        });
        this.activities = response.data;
        // 添加一些模拟数据
        this.activities.forEach(activity => {
          activity.priority = Math.floor(Math.random() * 3) + 1; // 1-3优先级
          activity.estimated_time = ['1 小时', '2 小时', '3 小时', '4 小时'][Math.floor(Math.random() * 4)];
        });
      } catch (error) {
        console.error('获取任务失败', error);
        this.$alert(`错误: ${error.response?.data?.error || '网络错误'}`);
      } finally {
        this.loading = false;
      }
    },
    goToSubmit(activityId) {
      this.$router.push({ name: 'SubmitAssignment', params: { activity_id: activityId } });
    },
    goToDetail(activityId) {
      this.$router.push({ name: 'StudentActivityDetail', params: { activity_id: activityId } });
    },
    getPriorityColor(priority) {
      switch (priority) {
        case 1: return 'success';
        case 2: return 'warning';
        case 3: return 'error';
        default: return 'grey';
      }
    },
    getPriorityText(priority) {
      switch (priority) {
        case 1: return '低优先级';
        case 2: return '中优先级';
        case 3: return '高优先级';
        default: return '普通';
      }
    }
  }
};
</script>

<style scoped>
.activity-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
}

/* 页面头部样式 */
.page-header {
  position: relative;
  padding: 4rem 0 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

.page-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 100"><path d="M0,0v46.29c47.79,22.2,103.59,32.17,158,28,70.36-5.37,136.33-33.31,206.8-37.5C438.64,32.43,512.34,53.67,583,72.05c69.27,18,138.3,24.88,209.4,13.08,36.15-6,69.85-17.84,104.45-29.34C989.49,25,1052,6.58,1000,0V0z" fill="%23ffffff" fill-opacity="0.1"/></svg>') repeat-x;
  background-size: 100% 100px;
  bottom: -1px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  position: relative;
  z-index: 2;
}

.title-wrapper {
  text-align: center;
}

.title-decoration {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.decoration-line {
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
  margin: 0 1rem;
}

.title-icon {
  background: rgba(255,255,255,0.2);
  padding: 0.5rem;
  border-radius: 50%;
  backdrop-filter: blur(10px);
}

.page-title {
  font-size: 3rem;
  font-weight: 800;
  color: white;
  margin: 0;
  text-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

.page-subtitle {
  font-size: 1.2rem;
  color: rgba(255,255,255,0.9);
  margin: 0.5rem 0 0;
  font-weight: 300;
}

.floating-elements {
  position: absolute;
  top: 0;
  right: 0;
  width: 300px;
  height: 200px;
  pointer-events: none;
}

.element {
  position: absolute;
  background: rgba(255,255,255,0.1);
  border-radius: 50%;
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: float 6s ease-in-out infinite;
}

.element-1 {
  top: 20px;
  right: 50px;
  width: 50px;
  height: 50px;
  animation-delay: 0s;
}

.element-2 {
  top: 80px;
  right: 120px;
  width: 40px;
  height: 40px;
  animation-delay: 2s;
}

.element-3 {
  top: 140px;
  right: 30px;
  width: 35px;
  height: 35px;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

/* 主要内容区域 */
.main-content {
  background: #f8fafc;
  min-height: calc(100vh - 200px);
  position: relative;
  z-index: 1;
}

.activity-content {
  padding: 2rem 0;
  max-width: 1200px;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #666;
}

.loading-text {
  margin-top: 1rem;
  font-size: 1.1rem;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  margin-bottom: 2rem;
}

.empty-title {
  font-size: 1.5rem;
  color: #374151;
  margin-bottom: 0.5rem;
}

.empty-subtitle {
  color: #6b7280;
  font-size: 1rem;
}

/* 任务网格 */
.activity-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 2rem;
  padding: 0 1rem;
}

.activity-item {
  opacity: 0;
  transform: translateY(20px);
  animation: slideInUp 0.6s ease-out forwards;
}

@keyframes slideInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 任务卡片 */
.activity-card {
  background: white;
  border-radius: 16px;
  border: 1px solid rgba(0,0,0,0.08);
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  height: 100%;
}

.activity-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  border-color: #667eea;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 1.5rem 1rem;
}

.card-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(245, 87, 108, 0.3);
}

.activity-id-chip {
  font-weight: 600;
}

.card-content {
  padding: 0 1.5rem 1rem;
}

.activity-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 1rem;
  line-height: 1.4;
}

.activity-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.description-section {
  background: #f8fafc;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  border-left: 4px solid #f093fb;
}

.md-preview-container {
  max-height: 120px;
  overflow-y: auto;
  font-size: 0.875rem;
  color: #4b5563;
}

.priority-section {
  margin-bottom: 1rem;
}

.priority-chip {
  font-weight: 500;
}

.card-actions {
  display: flex;
  gap: 0.75rem;
  padding: 0 1.5rem 1.5rem;
}

.action-btn {
  flex: 1;
  height: 40px;
  border-radius: 8px;
  font-weight: 500;
  text-transform: none;
}

.primary-btn {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.card-hover-overlay {
  position: absolute;
  top: 0;
  right: 0;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border-radius: 0 16px 0 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.activity-card:hover .card-hover-overlay {
  opacity: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-title {
    font-size: 2.5rem;
  }
  
  .activity-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .header-content {
    flex-direction: column;
    text-align: center;
  }
  
  .floating-elements {
    display: none;
  }
}
</style>