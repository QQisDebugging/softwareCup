<template>
  <div class="brief-question-container">
    <!-- 答题结果区域 -->
    <div v-if="showAnswers" class="result-section">
      <v-card class="result-card" elevation="0">
        <div class="result-header">
          <v-icon color="success" size="32">mdi-check-circle</v-icon>
          <h3 class="result-title">答题完成</h3>
        </div>
        <div class="result-content">
          <div class="result-stats">
            <div class="stat-item correct">
              <div class="stat-icon">
                <v-icon color="white" size="20">mdi-check</v-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ correctAnswers }}</div>
                <div class="stat-label">答对题目</div>
              </div>
            </div>
            <div class="stat-item incorrect">
              <div class="stat-icon">
                <v-icon color="white" size="20">mdi-close</v-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ parsedQuestions.length - correctAnswers }}</div>
                <div class="stat-label">答错题目</div>
              </div>
            </div>
            <div class="stat-item score">
              <div class="stat-icon">
                <v-icon color="white" size="20">mdi-star</v-icon>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ Math.round((correctAnswers / parsedQuestions.length) * 100) }}%</div>
                <div class="stat-label">正确率</div>
              </div>
            </div>
          </div>
          <div class="result-note">
            <v-icon color="info" size="20">mdi-information</v-icon>
            <span>问答题评分基于答案相似度，结果仅供参考</span>
          </div>
        </div>
      </v-card>
    </div>

    <!-- 题目列表 -->
    <div class="questions-section">
      <div 
        v-for="(item, index) in parsedQuestions" 
        :key="index"
        class="question-item"
        :class="{ 'answered': showAnswers }"
      >
        <v-card class="question-card" elevation="0">
          <div class="question-header">
            <div class="question-number">
              <span>{{ index + 1 }}</span>
            </div>
            <div class="question-type">
              <v-chip size="small" color="warning" variant="tonal">
                问答题
              </v-chip>
            </div>
            <div class="question-status" v-if="showAnswers">
              <v-icon color="success" size="24">mdi-check-circle</v-icon>
            </div>
          </div>

          <div class="question-content">
            <div class="question-title">
              {{ item.题目 }}
            </div>

            <div class="answer-container">
              <div class="answer-label">
                <v-icon color="primary" size="18">mdi-pencil</v-icon>
                <span>我的答案</span>
              </div>
              <v-textarea 
                v-model="userAnswers[index]" 
                label="请输入您的答案"
                placeholder="请在此处输入您的详细答案..."
                :disabled="showAnswers"
                rows="4"
                variant="outlined"
                class="answer-input"
                :class="{ 'answered': showAnswers }"
              />
            </div>

            <!-- 答案解析 -->
            <div v-if="showAnswers" class="answer-analysis">
              <div class="analysis-header">
                <v-icon color="success" size="20">mdi-check-circle</v-icon>
                <span class="analysis-title">标准答案</span>
              </div>
              <div class="analysis-content">
                <div class="correct-answer">
                  <div class="answer-text">{{ item.答案 }}</div>
                </div>
                <div class="user-answer-compare">
                  <div class="compare-label">
                    <v-icon color="primary" size="16">mdi-account</v-icon>
                    <span>您的答案</span>
                  </div>
                  <div class="user-answer-text">
                    {{ userAnswers[index] || '未作答' }}
                  </div>
                </div>
                <div class="analysis-explanation" v-if="item.解析">
                  <div class="explanation-label">
                    <v-icon color="info" size="16">mdi-lightbulb</v-icon>
                    <span>解题思路</span>
                  </div>
                  <p>{{ item.解析 }}</p>
                </div>
              </div>
            </div>
          </div>
        </v-card>
      </div>
    </div>

    <!-- 提交按钮 -->
    <div class="submit-section" v-if="!showAnswers">
      <v-card class="submit-card" elevation="0">
        <div class="submit-content">
          <div class="submit-info">
            <h4>准备提交答案</h4>
            <p>问答题将根据答案的完整性和准确性进行评分</p>
          </div>
          <v-btn 
            color="warning" 
            size="large"
            @click="submit"
            class="submit-btn"
            :disabled="!hasAnswers"
          >
            <v-icon start>mdi-send</v-icon>
            提交答案
          </v-btn>
        </div>
      </v-card>
    </div>
  </div>
</template>

<script>
import axios from '@/utils/axiosConfig';
import { pushRequestTimes } from '@/utils/commonUtil';

export default {
  name: 'BriefQuestionListStudent',
  props: {
    questionsJson: {
      type: String,
      required: true
    },
    contest_id: {
      type: String,
      required: true
    },
  },
  data() {
    return {
      userAnswers: {},
      showAnswers: false,
      correctAnswers: 0
    };
  },
  computed: {
    parsedQuestions() {
      return JSON.parse(this.questionsJson);
    },
    hasAnswers() {
      return Object.values(this.userAnswers).some(answer => answer && answer.trim().length > 0);
    }
  },
  methods: {
    async submit() {
      this.correctAnswers = this.calculateCorrectAnswers();
      this.showAnswers = true;

      const data = {
        contest_id: this.contest_id,
        sno: localStorage.getItem("username"),
        answers: this.userAnswers,
        question_type: '问答题',
        score: this.correctAnswers * 5
      };

      try {
        await axios.post(`${this.$backendUrl}/api/submitContestAnswers`, data);
        pushRequestTimes(1);
      } catch (error) {
        console.error('提交失败', error);
      }
    },
    calculateCorrectAnswers() {
      // 简单的字符串相似度比较
      let correct = 0;
      for (const [index, userAnswer] of Object.entries(this.userAnswers)) {
        if (userAnswer && userAnswer.trim().length > 0) {
          const standardAnswer = this.parsedQuestions[index].答案;
          // 简单的相似度计算：如果用户答案包含标准答案中的关键词，则认为正确
          if (this.calculateSimilarity(userAnswer, standardAnswer) > 0.3) {
            correct++;
          }
        }
      }
      return correct;
    },
    calculateSimilarity(userAnswer, standardAnswer) {
      if (!userAnswer || !standardAnswer) return 0;
      
      const userWords = userAnswer.toLowerCase().split(/\s+/);
      const standardWords = standardAnswer.toLowerCase().split(/\s+/);
      
      let matchCount = 0;
      userWords.forEach(word => {
        if (standardWords.includes(word) && word.length > 1) {
          matchCount++;
        }
      });
      
      return matchCount / Math.max(userWords.length, standardWords.length);
    }
  }
};
</script>

<style scoped>
.brief-question-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 1rem;
}

/* 答题结果区域 */
.result-section {
  margin-bottom: 2rem;
}

.result-card {
  background: white;
  border-radius: 16px;
  border: 1px solid rgba(0,0,0,0.08);
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.result-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.result-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.result-content {
  padding: 2rem;
}

.result-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 12px;
  transition: transform 0.2s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
}

.stat-item.correct {
  background: linear-gradient(135deg, #10b981, #059669);
}

.stat-item.incorrect {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.stat-item.score {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.stat-icon {
  background: rgba(255,255,255,0.2);
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  color: white;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.stat-label {
  font-size: 0.875rem;
  opacity: 0.9;
}

.result-note {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 8px;
  border-left: 4px solid #3b82f6;
  color: #1e40af;
  font-size: 0.875rem;
}

/* 题目列表 */
.questions-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin-bottom: 2rem;
}

.question-item {
  opacity: 0;
  transform: translateY(20px);
  animation: slideInUp 0.6s ease-out forwards;
}

.question-item:nth-child(1) { animation-delay: 0.1s; }
.question-item:nth-child(2) { animation-delay: 0.2s; }
.question-item:nth-child(3) { animation-delay: 0.3s; }
.question-item:nth-child(4) { animation-delay: 0.4s; }
.question-item:nth-child(5) { animation-delay: 0.5s; }

@keyframes slideInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.question-card {
  background: white;
  border-radius: 16px;
  border: 1px solid rgba(0,0,0,0.08);
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.question-card:hover {
  box-shadow: 0 8px 30px rgba(0,0,0,0.1);
}

.question-item.answered .question-card {
  border-color: #f59e0b;
  background: linear-gradient(135deg, #fffbeb 0%, #ffffff 100%);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.question-number {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 1.125rem;
}

.question-content {
  padding: 2rem;
}

.question-title {
  font-size: 1.125rem;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.answer-container {
  margin-bottom: 2rem;
}

.answer-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-weight: 500;
  color: #374151;
}

.answer-input {
  transition: all 0.3s ease;
}

.answer-input.answered :deep(.v-field) {
  background: rgba(245, 158, 11, 0.05);
  border-color: #f59e0b;
}

.answer-input :deep(.v-field__field) {
  font-size: 0.95rem;
  line-height: 1.5;
}

.answer-input :deep(.v-field__input) {
  padding: 1rem;
}

/* 答案解析 */
.answer-analysis {
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
  border-radius: 12px;
  padding: 2rem;
  border-left: 4px solid #f59e0b;
  margin-top: 2rem;
}

.analysis-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.analysis-title {
  font-weight: 600;
  color: #92400e;
  font-size: 1.125rem;
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.correct-answer {
  background: rgba(16, 185, 129, 0.1);
  border-radius: 8px;
  padding: 1.5rem;
  border-left: 3px solid #10b981;
}

.answer-text {
  font-size: 1rem;
  line-height: 1.6;
  color: #065f46;
  font-weight: 500;
}

.user-answer-compare {
  background: rgba(59, 130, 246, 0.1);
  border-radius: 8px;
  padding: 1.5rem;
  border-left: 3px solid #3b82f6;
}

.compare-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  font-weight: 500;
  color: #1e40af;
}

.user-answer-text {
  font-size: 1rem;
  line-height: 1.6;
  color: #1e3a8a;
  font-style: italic;
}

.analysis-explanation {
  background: rgba(139, 69, 19, 0.1);
  border-radius: 8px;
  padding: 1.5rem;
  border-left: 3px solid #92400e;
}

.explanation-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  font-weight: 500;
  color: #92400e;
}

.analysis-explanation p {
  font-size: 0.95rem;
  line-height: 1.6;
  color: #78350f;
  margin: 0;
}

/* 提交区域 */
.submit-section {
  position: sticky;
  bottom: 2rem;
  z-index: 10;
}

.submit-card {
  background: white;
  border-radius: 16px;
  border: 1px solid rgba(0,0,0,0.08);
  box-shadow: 0 8px 30px rgba(0,0,0,0.15);
  overflow: hidden;
}

.submit-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
}

.submit-info h4 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 0.5rem;
}

.submit-info p {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.submit-btn {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
  text-transform: none;
  font-weight: 500;
  padding: 0 2rem;
  height: 48px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.submit-btn:hover {
  box-shadow: 0 6px 16px rgba(245, 158, 11, 0.4);
}

.submit-btn:disabled {
  background: #e5e7eb;
  color: #9ca3af;
  box-shadow: none;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .brief-question-container {
    padding: 0.5rem;
  }
  
  .result-stats {
    grid-template-columns: 1fr;
  }
  
  .submit-content {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .question-header {
    padding: 1rem;
  }
  
  .question-content {
    padding: 1.5rem;
  }
  
  .analysis-content {
    gap: 1rem;
  }
  
  .answer-analysis {
    padding: 1.5rem;
  }
}
</style>
