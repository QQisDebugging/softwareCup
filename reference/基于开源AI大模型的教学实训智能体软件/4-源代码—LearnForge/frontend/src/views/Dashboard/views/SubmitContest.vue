<template>
  <div class="submit-contest-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-main">
          <div class="title-wrapper">
            <div class="title-decoration">
              <div class="decoration-line"></div>
              <v-icon class="title-icon" color="white" size="40">mdi-pencil-box</v-icon>
              <div class="decoration-line"></div>
            </div>
            <h1 class="page-title">开始答题</h1>
            <p class="page-subtitle">展示你的学习成果</p>
          </div>
        </div>
        <div class="header-decoration">
          <div class="floating-elements">
            <div class="element element-1">
              <v-icon color="white" size="24">mdi-brain</v-icon>
            </div>
            <div class="element element-2">
              <v-icon color="white" size="20">mdi-check-bold</v-icon>
            </div>
            <div class="element element-3">
              <v-icon color="white" size="18">mdi-timer</v-icon>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <v-container class="contest-content">
        <!-- 作业信息卡片 -->
        <div v-if="contest" class="contest-info-section">
          <v-card class="contest-info-card" elevation="0">
            <div class="card-header">
              <div class="contest-icon">
                <v-icon color="white" size="32">{{ getQuestionTypeIcon(contest.question_type) }}</v-icon>
              </div>
              <div class="contest-meta">
                <h2 class="contest-name">{{ contest.contest_name }}</h2>
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
              </div>
            </div>
            
            <div class="contest-stats">
              <div class="stat-item">
                <div class="stat-icon">
                  <v-icon color="primary" size="20">mdi-format-list-numbered</v-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-number">{{ getQuestionCount() }}</div>
                  <div class="stat-label">题目数量</div>
                </div>
              </div>
              <div class="stat-item">
                <div class="stat-icon">
                  <v-icon color="success" size="20">mdi-star</v-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-number">{{ getEstimatedTime() }}</div>
                  <div class="stat-label">预计时间</div>
                </div>
              </div>
              <div class="stat-item">
                <div class="stat-icon">
                  <v-icon color="warning" size="20">mdi-medal</v-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-number">100</div>
                  <div class="stat-label">满分</div>
                </div>
              </div>
            </div>
          </v-card>
        </div>

        <!-- 答题提示 -->
        <div class="tips-section">
          <v-card class="tips-card" elevation="0">
            <div class="tips-header">
              <v-icon color="info" size="24">mdi-lightbulb</v-icon>
              <h3 class="tips-title">答题提示</h3>
            </div>
            <div class="tips-content">
              <div class="tip-item">
                <v-icon color="success" size="16">mdi-check-circle</v-icon>
                <span>仔细阅读题目，理解题意后再作答</span>
              </div>
              <div class="tip-item">
                <v-icon color="warning" size="16">mdi-clock-alert</v-icon>
                <span>合理安排时间，避免在单题上花费过多时间</span>
              </div>
              <div class="tip-item">
                <v-icon color="info" size="16">mdi-bookmark-check</v-icon>
                <span>答题完成后请仔细检查，确认无误后提交</span>
              </div>
            </div>
          </v-card>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <v-progress-circular
            indeterminate
            color="primary"
            size="64"
          ></v-progress-circular>
          <p class="loading-text">正在加载题目...</p>
        </div>

        <!-- 空状态 -->
        <div v-else-if="!contest" class="empty-state">
          <div class="empty-icon">
            <v-icon size="80" color="grey-lighten-2">mdi-file-question-outline</v-icon>
          </div>
          <h3 class="empty-title">未找到作业信息</h3>
          <p class="empty-subtitle">作业可能已被删除或不存在</p>
          <v-btn 
            color="primary" 
            @click="$router.go(-1)"
            class="back-btn"
          >
            返回上一页
          </v-btn>
        </div>

        <!-- 答题区域 -->
        <div v-else class="question-section">
          <v-card class="question-card" elevation="0">
            <div class="question-header">
              <div class="question-title">
                <v-icon color="primary" size="28">mdi-clipboard-text</v-icon>
                <h3>开始答题</h3>
              </div>
              <div class="question-progress">
                <v-chip color="primary" variant="tonal">
                  {{ contest.question_type }}
                </v-chip>
              </div>
            </div>
            
            <div class="question-content">
              <component 
                :is="questionComponent" 
                :contest_id="contest.contest_id" 
                :contest_type="contest.question_type" 
                :questionsJson="contest.question_json" 
                v-if="contest && questionComponent"
              />
            </div>
          </v-card>
        </div>
      </v-container>
    </div>
  </div>
</template>

<script>
import axios from '@/utils/axiosConfig';
import BriefQuestionListStudent from '@/components/BriefQuestionListStudent.vue';
import ChoiceQuestionListStudent from '@/components/ChoiceQuestionListStudent.vue';
import JudgeQuestionListStudent from '@/components/JudgeQuestionListStudent.vue';
import moment from 'moment';

export default {
  name: 'SubmitContest',
  props: ['contest_id'],
  components: {
    ChoiceQuestionListStudent,
    JudgeQuestionListStudent,
    BriefQuestionListStudent
  },
  data() {
    return {
      contest: null,
      questionComponent: null,
      loading: true
    };
  },
  created() {
    this.loadContest();
  },
  methods: {
    formattedSubmissionDate(submissionDate) {
      return moment(submissionDate).format('YYYY-MM-DD HH:mm');
    },
    async loadContest() {
      this.loading = true;
      try {
        const response = await axios.get(`${this.$backendUrl}/api/getContestDetailsById`, {
          params: { contest_id: this.contest_id }
        });
        this.contest = response.data;
        this.loadQuestionComponent();
      } catch (error) {
        console.error('获取竞赛信息失败', error);
      } finally {
        this.loading = false;
      }
    },
    loadQuestionComponent() {
      switch (this.contest.question_type) {
        case '选择题':
          this.questionComponent = ChoiceQuestionListStudent;
          break;
        case '判断题':
          this.questionComponent = JudgeQuestionListStudent;
          break;
        case '问答题':
          this.questionComponent = BriefQuestionListStudent;
          break;
        default:
          this.questionComponent = null;
      }
    },
    getQuestionTypeIcon(type) {
      switch (type) {
        case '选择题': return 'mdi-format-list-bulleted-type';
        case '判断题': return 'mdi-check-circle-outline';
        case '问答题': return 'mdi-text-box-outline';
        default: return 'mdi-help-circle-outline';
      }
    },
    getQuestionCount() {
      if (!this.contest || !this.contest.question_json) return 0;
      try {
        const questions = JSON.parse(this.contest.question_json);
        return questions.length;
      } catch (error) {
        return 0;
      }
    },
    getEstimatedTime() {
      const count = this.getQuestionCount();
      if (count === 0) return '0分钟';
      
      // 根据题目类型估算时间
      let timePerQuestion = 2; // 默认每题2分钟
      switch (this.contest.question_type) {
        case '选择题':
          timePerQuestion = 1;
          break;
        case '判断题':
          timePerQuestion = 0.5;
          break;
        case '问答题':
          timePerQuestion = 3;
          break;
      }
      
      const totalMinutes = Math.ceil(count * timePerQuestion);
      return totalMinutes >= 60 ? `${Math.floor(totalMinutes / 60)}小时${totalMinutes % 60}分钟` : `${totalMinutes}分钟`;
    }
  }
};
</script>

<style scoped>
.submit-contest-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
}

/* 页面头部样式 */
.page-header {
  position: relative;
  padding: 3rem 0 2rem;
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
  font-size: 2.5rem;
  font-weight: 800;
  color: white;
  margin: 0;
  text-shadow: 0 2px 10px rgba(0,0,0,0.2);
}

.page-subtitle {
  font-size: 1.1rem;
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
  min-height: calc(100vh - 180px);
  position: relative;
  z-index: 1;
}

.contest-content {
  padding: 2rem 0;
  max-width: 1000px;
}

/* 作业信息卡片 */
.contest-info-section {
  margin-bottom: 2rem;
}

.contest-info-card {
  background: white;
  border-radius: 16px;
  border: 1px solid rgba(0,0,0,0.08);
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.card-header {
  display: flex;
  align-items: center;
  padding: 2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.contest-icon {
  background: linear-gradient(135deg, #667eea, #764ba2);
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1.5rem;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.contest-meta {
  flex: 1;
}

.contest-name {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem;
}

.contest-details {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.contest-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  padding: 2rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafc;
  border-radius: 12px;
  transition: transform 0.2s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
}

.stat-icon {
  background: white;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* 答题提示 */
.tips-section {
  margin-bottom: 2rem;
}

.tips-card {
  background: white;
  border-radius: 16px;
  border: 1px solid rgba(0,0,0,0.08);
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.tips-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.tips-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.tips-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #4b5563;
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
  margin-bottom: 2rem;
}

.back-btn {
  text-transform: none;
  font-weight: 500;
}

/* 答题区域 */
.question-section {
  margin-bottom: 2rem;
}

.question-card {
  background: white;
  border-radius: 16px;
  border: 1px solid rgba(0,0,0,0.08);
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.question-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.question-title h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.question-progress {
  display: flex;
  gap: 0.5rem;
}

.question-content {
  padding: 2rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }
  
  .header-content {
    flex-direction: column;
    text-align: center;
  }
  
  .floating-elements {
    display: none;
  }
  
  .card-header {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .contest-icon {
    margin-right: 0;
  }
  
  .contest-details {
    justify-content: center;
  }
  
  .contest-stats {
    grid-template-columns: 1fr;
  }
}
</style>
  