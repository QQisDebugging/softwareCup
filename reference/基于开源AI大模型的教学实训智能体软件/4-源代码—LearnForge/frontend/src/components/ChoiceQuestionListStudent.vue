<template>
  <div class="choice-question-container">
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
        </div>
      </v-card>
    </div>

    <!-- 题目列表 -->
    <div class="questions-section">
      <div 
        v-for="(item, index) in parsedQuestions" 
        :key="index"
        class="question-item"
        :class="{ 'answered': showAnswers, 'correct': showAnswers && selectedAnswers[index] === item.答案, 'incorrect': showAnswers && selectedAnswers[index] !== item.答案 }"
      >
        <v-card class="question-card" elevation="0">
          <div class="question-header">
            <div class="question-number">
              <span>{{ index + 1 }}</span>
            </div>
            <div class="question-type">
              <v-chip size="small" color="primary" variant="tonal">
                选择题
              </v-chip>
            </div>
            <div class="question-status" v-if="showAnswers">
              <v-icon 
                :color="selectedAnswers[index] === item.答案 ? 'success' : 'error'"
                size="24"
              >
                {{ selectedAnswers[index] === item.答案 ? 'mdi-check-circle' : 'mdi-close-circle' }}
              </v-icon>
            </div>
          </div>

          <div class="question-content">
            <div class="question-title">
              {{ item.题目 }}
            </div>

            <div class="options-container">
              <v-radio-group 
                v-model="selectedAnswers[index]" 
                class="answer-options"
                :disabled="showAnswers"
              >
                <div 
                  v-for="(option, optionIndex) in item.选项" 
                  :key="optionIndex"
                  class="option-item"
                  :class="{ 
                    'selected': selectedAnswers[index] === optionIndex,
                    'correct': showAnswers && optionIndex === item.答案,
                    'incorrect': showAnswers && selectedAnswers[index] === optionIndex && optionIndex !== item.答案
                  }"
                >
                  <v-radio 
                    :label="option"
                    :value="optionIndex"
                    class="option-radio"
                  />
                </div>
              </v-radio-group>
            </div>

            <!-- 答案解析 -->
            <div v-if="showAnswers" class="answer-analysis">
              <div class="analysis-header">
                <v-icon color="info" size="20">mdi-information</v-icon>
                <span class="analysis-title">正确答案</span>
              </div>
              <div class="analysis-content">
                <div class="correct-answer">
                  <strong>{{ String.fromCharCode(65 + item.答案) }}. {{ item.选项[item.答案] }}</strong>
                </div>
                <div class="analysis-explanation" v-if="item.解析">
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
            <p>请确认所有题目都已作答，提交后将无法修改答案</p>
          </div>
          <v-btn 
            color="primary" 
            size="large"
            @click="submit"
            class="submit-btn"
            :disabled="!isAllAnswered"
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
  name: 'ChoiceQuestionListStudent',
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
      selectedAnswers: {},
      showAnswers: false,
      correctAnswers: 0
    };
  },
  computed: {
    parsedQuestions() {
      return JSON.parse(this.questionsJson);
    },
    isAllAnswered() {
      return Object.keys(this.selectedAnswers).length === this.parsedQuestions.length;
    }
  },
  methods: {
    submit() {
      this.showAnswers = true;
      this.correctAnswers = this.calculateCorrectAnswers();
      this.submitAnswersToServer();
    },
    calculateCorrectAnswers() {
      let correct = 0;
      for (const [index, selected] of Object.entries(this.selectedAnswers)) {
        if (parseInt(selected) === this.parsedQuestions[index].答案) {
          correct++;
        }
      }
      return correct;
    },
    submitAnswersToServer() {
      const data = {
        answers: this.selectedAnswers,
        sno: localStorage.getItem("username"),
        contest_id: this.contest_id,
        question_type: '选择题',
        score: this.correctAnswers * 5
      };
      
      axios.post(`${this.$backendUrl}/submitContestAnswers`, data)
        .then(response => {
          pushRequestTimes(1);
        })
        .catch(error => {
          console.error('提交答题情况时出现错误:', error);
        });
    }
  }
};
</script>

<style scoped>
.choice-question-container {
  max-width: 900px;
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

.question-item.answered.correct .question-card {
  border-color: #10b981;
  background: linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%);
}

.question-item.answered.incorrect .question-card {
  border-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2 0%, #ffffff 100%);
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
  background: linear-gradient(135deg, #667eea, #764ba2);
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
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.options-container {
  margin-bottom: 1.5rem;
}

.answer-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.option-item {
  padding: 1rem;
  border-radius: 12px;
  border: 2px solid transparent;
  background: #f8fafc;
  transition: all 0.2s ease;
  cursor: pointer;
}

.option-item:hover {
  background: #f1f5f9;
  border-color: #e2e8f0;
}

.option-item.selected {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.option-item.correct {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}

.option-item.incorrect {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.option-radio {
  width: 100%;
}

.option-radio :deep(.v-label) {
  font-weight: 500;
  color: #374151;
}

/* 答案解析 */
.answer-analysis {
  background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%);
  border-radius: 12px;
  padding: 1.5rem;
  border-left: 4px solid #3b82f6;
}

.analysis-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.analysis-title {
  font-weight: 600;
  color: #1e40af;
}

.analysis-content {
  color: #374151;
}

.correct-answer {
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 8px;
  border-left: 3px solid #10b981;
}

.analysis-explanation {
  font-size: 0.875rem;
  line-height: 1.5;
  color: #6b7280;
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
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  text-transform: none;
  font-weight: 500;
  padding: 0 2rem;
  height: 48px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.submit-btn:hover {
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  background: #e5e7eb;
  color: #9ca3af;
  box-shadow: none;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .choice-question-container {
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
}
</style>
