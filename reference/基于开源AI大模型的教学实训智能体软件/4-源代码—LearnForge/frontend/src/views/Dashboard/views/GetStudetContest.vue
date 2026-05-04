<template>
  <div class="contest-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-main">
          <div class="title-wrapper">
            <div class="title-decoration">
              <div class="decoration-line"></div>
              <v-icon class="title-icon" color="white" size="40">mdi-trophy</v-icon>
              <div class="decoration-line"></div>
            </div>
            <h1 class="page-title gradient-text">我的作业</h1>
            <p class="page-subtitle">挑战题目，展示学习成果</p>
          </div>
        </div>
        <div class="header-decoration">
          <div class="floating-elements">
            <div class="element element-1">
              <v-icon color="white" size="24">mdi-medal</v-icon>
            </div>
            <div class="element element-2">
              <v-icon color="white" size="20">mdi-pencil</v-icon>
            </div>
            <div class="element element-3">
              <v-icon color="white" size="18">mdi-check-circle</v-icon>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <v-container class="contest-content">
        <!-- 统计信息 -->
        <div class="stats-section">
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-icon completed">
                <v-icon color="white" size="24">mdi-check-circle</v-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ completedCount }}</div>
                <div class="stat-label">已完成</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon pending">
                <v-icon color="white" size="24">mdi-clock-outline</v-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ pendingCount }}</div>
                <div class="stat-label">待完成</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon total">
                <v-icon color="white" size="24">mdi-sigma</v-icon>
              </div>
              <div class="stat-content">
                <div class="stat-number">{{ contests.length }}</div>
                <div class="stat-label">总计</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <v-progress-circular
            indeterminate
            color="primary"
            size="64"
          ></v-progress-circular>
          <p class="loading-text">正在加载作业数据...</p>
        </div>

        <!-- 空状态 -->
        <div v-else-if="!contests.length" class="empty-state">
          <div class="empty-icon">
            <v-icon size="80" color="grey-lighten-2">mdi-trophy-outline</v-icon>
          </div>
          <h3 class="empty-title">暂无作业</h3>
          <p class="empty-subtitle">老师还没有发布作业，请稍后再来查看</p>
        </div>

        <!-- 作业列表 -->
        <div v-else class="contest-grid">
          <div 
            v-for="(contest, index) in contests" 
            :key="contest.contest_id"
            class="contest-item"
            :style="{ animationDelay: `${index * 0.1}s` }"
          >
            <v-card
              class="contest-card"
              :class="{ 'completed': contest.isDone }"
              elevation="0"
              @click="goToDetail(contest.contest_id)"
            >
              <div class="card-header">
                <div class="card-icon">
                  <v-icon color="white" size="32">
                    {{ getQuestionTypeIcon(contest.question_type) }}
                  </v-icon>
                </div>
                <div class="card-meta">
                  <v-chip
                    size="small"
                    :color="contest.isDone ? 'success' : 'warning'"
                    variant="flat"
                    class="status-chip"
                  >
                    <v-icon size="12" start>
                      {{ contest.isDone ? 'mdi-check' : 'mdi-clock' }}
                    </v-icon>
                    {{ contest.isDone ? '已完成' : '待完成' }}
                  </v-chip>
                </div>
              </div>

              <div class="card-content">
                <h3 class="contest-title">{{ contest.contest_name }}</h3>
                
                <div class="contest-details">
                  <div class="detail-item">
                    <v-icon size="16" color="grey-darken-1">mdi-identifier</v-icon>
                    <span>编号: {{ contest.contest_id }}</span>
                  </div>
                  <div class="detail-item">
                    <v-icon size="16" color="grey-darken-1">mdi-calendar</v-icon>
                    <span>{{ formattedSubmissionDate(contest.publish_date) }}</span>
                  </div>
                  <div class="detail-item">
                    <v-icon size="16" color="grey-darken-1">mdi-file-question</v-icon>
                    <span>{{ contest.question_type }}</span>
                  </div>
                </div>

                <div class="difficulty-section">
                  <div class="difficulty-info">
                    <span class="difficulty-label">难度等级</span>
                    <v-chip
                      size="small"
                      :color="getDifficultyColor(contest.difficulty)"
                      variant="tonal"
                    >
                      {{ getDifficultyText(contest.difficulty) }}
                    </v-chip>
                  </div>
                  <div class="score-info" v-if="contest.score">
                    <span class="score-label">得分</span>
                    <span class="score-value">{{ contest.score }}/100</span>
                  </div>
                </div>
              </div>

              <div class="card-actions">
                <v-btn
                  variant="outlined"
                  color="primary"
                  size="small"
                  @click.stop="goToDetail(contest.contest_id)"
                  class="action-btn"
                >
                  <v-icon size="16" start>mdi-eye</v-icon>
                  查看详情
                </v-btn>
                <v-btn
                  :color="contest.isDone ? 'grey' : 'primary'"
                  size="small"
                  :disabled="contest.isDone"
                  @click.stop="goToSubmit(contest.contest_id)"
                  class="action-btn primary-btn"
                >
                  <v-icon size="16" start>
                    {{ contest.isDone ? 'mdi-check' : 'mdi-pencil' }}
                  </v-icon>
                  {{ contest.isDone ? '已完成' : '开始答题' }}
                </v-btn>
              </div>

              <div class="card-hover-overlay" v-if="!contest.isDone">
                <v-icon size="24" color="white">mdi-arrow-right</v-icon>
              </div>

              <!-- 完成标记 -->
              <div class="completion-badge" v-if="contest.isDone">
                <v-icon color="success" size="20">mdi-check-circle</v-icon>
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
  name: 'GetStudentContest',
  data() {
    return {
      contests: [],
      loading: true,
      sno: localStorage.getItem('username'),
    };
  },
  computed: {
    completedCount() {
      return this.contests.filter(c => c.isDone).length;
    },
    pendingCount() {
      return this.contests.filter(c => !c.isDone).length;
    }
  },
  mounted() {
    this.fetchStudentContests();
  },
  methods: {
    formattedSubmissionDate(submissionDate) {
      return moment(submissionDate).format('YYYY-MM-DD HH:mm');
    },
    async fetchStudentContests() {
      this.loading = true;
      try {
        const response = await axios.get(`${this.$backendUrl}/api/getStudentContests`, {
          params: { sno: this.sno }
        });
        this.contests = response.data;
        // 添加一些模拟数据
        this.contests.forEach(contest => {
          contest.difficulty = Math.floor(Math.random() * 3) + 1; // 1-3难度
          if (contest.isDone) {
            contest.score = Math.floor(Math.random() * 41) + 60; // 60-100分
          }
        });
      } catch (error) {
        console.error('获取作业失败', error);
        this.$alert(`错误: ${error.response?.data?.error || '网络错误'}`);
      } finally {
        this.loading = false;
      }
    },
    goToSubmit(contestId) {
      this.$router.push({ name: 'SubmitContest', params: { contest_id: contestId } });
    },
    goToDetail(contestId) {
      this.$router.push({ name: 'StudentContestDetail', params: { contest_id: contestId } });
    },
    getQuestionTypeIcon(type) {
      switch (type) {
        case '选择题': return 'mdi-format-list-bulleted-type';
        case '判断题': return 'mdi-check-circle-outline';
        case '问答题': return 'mdi-text-box-outline';
        default: return 'mdi-help-circle-outline';
      }
    },
    getDifficultyColor(difficulty) {
      switch (difficulty) {
        case 1: return 'success';
        case 2: return 'warning';
        case 3: return 'error';
        default: return 'grey';
      }
    },
    getDifficultyText(difficulty) {
      switch (difficulty) {
        case 1: return '简单';
        case 2: return '中等';
        case 3: return '困难';
        default: return '未知';
      }
    }
  }
};
</script>

<style scoped>
.contest-container {
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

.contest-content {
  padding: 2rem 0;
  max-width: 1200px;
}

/* 统计信息 */
.stats-section {
  margin-bottom: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-item {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  transition: transform 0.2s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.completed {
  background: linear-gradient(135deg, #10b981, #059669);
}

.stat-icon.pending {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.stat-icon.total {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
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

/* 作业网格 */
.contest-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
  padding: 0 1rem;
}

.contest-item {
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

/* 作业卡片 */
.contest-card {
  background: white;
  border-radius: 16px;
  border: 1px solid rgba(0,0,0,0.08);
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  height: 100%;
}

.contest-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
  border-color: #667eea;
}

.contest-card.completed {
  background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
  border-color: #10b981;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 1.5rem 1rem;
}

.card-icon {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.status-chip {
  font-weight: 600;
  color: white;
}

.card-content {
  padding: 0 1.5rem 1rem;
}

.contest-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 1rem;
  line-height: 1.4;
}

.contest-details {
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

.difficulty-section {
  background: #f8fafc;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.difficulty-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.difficulty-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.score-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.score-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.score-value {
  font-size: 1rem;
  font-weight: 600;
  color: #10b981;
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
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  color: white;
}

.primary-btn:disabled {
  background: #e5e7eb;
  color: #9ca3af;
}

.card-hover-overlay {
  position: absolute;
  top: 0;
  right: 0;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  border-radius: 0 16px 0 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.contest-card:hover .card-hover-overlay {
  opacity: 1;
}

.completion-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: white;
  border-radius: 50%;
  padding: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-title {
    font-size: 2.5rem;
  }
  
  .contest-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
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