<template>
    <div class="completion-container">
      <v-container class="completion-content">
        <v-row justify="center">
          <v-col cols="12" sm="8" md="6" lg="4">
            <v-card class="completion-card" elevation="12">
              <v-card-text class="text-center completion-text">
                <div class="celebration-icon">
                  <v-icon color="success" size="80">mdi-trophy</v-icon>
                </div>
                <h1 class="completion-title">恭喜完成！</h1>
                <p class="completion-message">你已经成功完成了今日的每日一测</p>
                
                <div class="stats-container">
                  <div class="stat-item">
                    <v-icon color="primary" size="24">mdi-clock-outline</v-icon>
                    <div class="stat-value">{{ timeSpent }}</div>
                    <div class="stat-label">分钟</div>
                  </div>
                  <div class="stat-item">
                    <v-icon color="success" size="24">mdi-check-circle</v-icon>
                    <div class="stat-value">100%</div>
                    <div class="stat-label">完成度</div>
                  </div>
                </div>
                
                <div class="encouragement">
                  <p class="encouragement-text">
                    <v-icon color="warning" size="20" class="mr-2">mdi-star</v-icon>
                    坚持每日练习，编程能力稳步提升！
                  </p>
                </div>
                
                <div class="action-buttons">
                  <v-btn
                    color="primary"
                    size="large"
                    @click="goToStudentArea"
                    class="action-btn"
                  >
                    <v-icon start>mdi-home</v-icon>
                    返回学习中心
                  </v-btn>
                  <v-btn
                    color="success"
                    size="large"
                    @click="startNewTest"
                    class="action-btn"
                    variant="outlined"
                  >
                    <v-icon start>mdi-refresh</v-icon>
                    再次挑战
                  </v-btn>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        timeSpent: 0 // 用来存储做题时长
      };
    },
    mounted () {
      // 假设父组件传递了做题时长过来
      this.timeSpent = this.$route.params.timeSpent || 0;
    },
    methods: {
      goToStudentArea() {
        this.$router.push({ name: 'StudentArea' });
      },
      startNewTest() {
        this.$router.push({ name: 'DailyTest' });
      }
    }
  };
  </script>
  
  <style scoped>
  .completion-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }
  
  .completion-content {
    width: 100%;
    max-width: 600px;
  }
  
  .completion-card {
    background: white;
    border-radius: 24px;
    padding: 40px 20px;
    animation: slideInUp 0.6s ease-out;
  }
  
  .completion-text {
    padding: 0;
  }
  
  .celebration-icon {
    margin-bottom: 24px;
    animation: bounce 2s infinite;
  }
  
  .completion-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #2c3e50;
    margin-bottom: 16px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .completion-message {
    font-size: 1.2rem;
    color: #666;
    margin-bottom: 32px;
  }
  
  .stats-container {
    display: flex;
    justify-content: center;
    gap: 32px;
    margin-bottom: 32px;
    padding: 24px;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 16px;
  }
  
  .stat-item {
    text-align: center;
  }
  
  .stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: #2c3e50;
    margin: 8px 0 4px;
  }
  
  .stat-label {
    font-size: 0.9rem;
    color: #666;
    font-weight: 500;
  }
  
  .encouragement {
    margin-bottom: 32px;
    padding: 20px;
    background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
    border-radius: 12px;
    border-left: 4px solid #ffd93d;
  }
  
  .encouragement-text {
    font-size: 1.1rem;
    color: #856404;
    font-weight: 500;
    margin: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .action-buttons {
    display: flex;
    gap: 16px;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .action-btn {
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
    transition: all 0.3s ease;
    min-width: 160px;
  }
  
  .action-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  }
  
  /* 动画效果 */
  @keyframes slideInUp {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  @keyframes bounce {
    0%, 20%, 50%, 80%, 100% {
      transform: translateY(0);
    }
    40% {
      transform: translateY(-10px);
    }
    60% {
      transform: translateY(-5px);
    }
  }
  
  /* 响应式设计 */
  @media (max-width: 768px) {
    .completion-title {
      font-size: 2rem;
    }
    
    .completion-message {
      font-size: 1rem;
    }
    
    .stats-container {
      gap: 16px;
      padding: 16px;
    }
    
    .stat-value {
      font-size: 1.5rem;
    }
    
    .encouragement-text {
      font-size: 1rem;
    }
    
    .action-buttons {
      flex-direction: column;
      align-items: center;
    }
    
    .action-btn {
      width: 100%;
      max-width: 200px;
    }
  }
  </style>
  