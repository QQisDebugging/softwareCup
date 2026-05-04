<template>
  <div class="create-work-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-main">
          <h1 class="page-title gradient-text">🚀 创建实训项目</h1>
          <p class="page-subtitle">基于AI智能生成实训任务，提升学生编程能力</p>
        </div>
        <div class="header-actions">
          <v-chip 
            v-if="tasks.length" 
            color="success" 
            variant="elevated"
            size="small"
          >
            已生成 {{ tasks.length }} 个任务
          </v-chip>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <v-container class="main-container">
      <!-- 任务生成表单 -->
      <v-card class="form-card" elevation="4">
        <v-card-title class="form-header">
          <v-icon color="primary" size="28" class="mr-3">mdi-robot</v-icon>
          <span class="form-title">AI智能生成实训任务</span>
        </v-card-title>
        
        <v-card-text class="form-content">
          <v-form ref="form" @submit.prevent="submitForm">
            <v-textarea
              label="实训项目描述"
              placeholder="请详细描述您想要创建的实训项目，例如：设计一个学生信息管理系统，包含增删改查功能..."
              v-model="designContent"
              :rules="contentRules"
              variant="outlined"
              rows="4"
              counter
              maxlength="500"
              required
              class="mb-4"
            >
              <template v-slot:prepend-inner>
                <v-icon color="primary">mdi-file-document-edit</v-icon>
              </template>
            </v-textarea>

            <div class="form-actions">
              <v-btn 
                type="submit" 
                color="primary" 
                size="large"
                :loading="loading"
                :disabled="loading || !designContent.trim()"
                prepend-icon="mdi-creation"
                class="generate-btn"
              >
                {{ loading ? '正在生成...' : '生成实训任务' }}
              </v-btn>
              
              <v-btn 
                v-if="tasks.length && !loading" 
                color="success" 
                size="large"
                @click="publish"
                prepend-icon="mdi-publish"
                class="publish-btn"
              >
                发布实训
              </v-btn>
            </div>
          </v-form>
        </v-card-text>
      </v-card>

      <!-- 错误信息显示 -->
      <v-alert
        v-if="error"
        type="error"
        variant="tonal"
        class="mt-4"
        closable
        @click:close="error = ''"
      >
        <v-icon slot="prepend">mdi-alert</v-icon>
        {{ error }}
      </v-alert>

      <!-- 生成的任务列表 -->
      <div v-if="tasks.length" class="tasks-section">
        <div class="section-header">
          <h2 class="section-title">📚 生成的实训任务</h2>
          <v-chip color="info" variant="elevated">
            共 {{ tasks.length }} 个知识点
          </v-chip>
        </div>

        <v-expansion-panels v-model="panel" multiple class="tasks-panels">
          <v-expansion-panel 
            v-for="(task, index) in tasks" 
            :key="index"
            class="task-panel"
          >
            <v-expansion-panel-title class="task-title">
              <div class="task-header">
                <v-chip color="primary" size="small" class="task-number">
                  {{ index + 1 }}
                </v-chip>
                <span class="knowledge-point">{{ task.知识点 }}</span>
              </div>
            </v-expansion-panel-title>
            
            <v-expansion-panel-text class="task-content">
              <div class="task-description">
                <h4 class="task-subtitle">📝 任务描述</h4>
                <div class="task-text">{{ task.题目 }}</div>
              </div>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </div>
    </v-container>

    <!-- 发布对话框 -->
    <v-dialog v-model="publishDialog" max-width="800" persistent>
      <v-card class="publish-card">
        <v-card-title class="publish-header">
          <v-icon color="success" size="32" class="mr-3">mdi-publish</v-icon>
          <span class="publish-title">发布实训项目</span>
          <v-spacer></v-spacer>
          <v-btn 
            icon="mdi-close" 
            @click="publishDialog = false"
            variant="text"
          ></v-btn>
        </v-card-title>
        
        <v-card-text class="publish-content">
          <v-form @submit.prevent="submitAssignment" ref="publishForm">
            <v-text-field
              label="实训项目名称"
              v-model="assignmentName"
              :rules="nameRules"
              variant="outlined"
              required
              class="mb-4"
              prepend-inner-icon="mdi-rename-box"
            ></v-text-field>
            
            <v-select
              v-model="selectedClasses"
              :items="classes"
              item-title="ClassName"
              item-value="ClassID"
              label="选择目标班级"
              multiple
              chips
              variant="outlined"
              closable-chips
              :rules="classRules"
              class="mb-4"
              prepend-inner-icon="mdi-account-group"
            >
              <template v-slot:chip="{ props, item }">
                <v-chip
                  v-bind="props"
                  :text="item.title"
                  color="primary"
                  variant="elevated"
                ></v-chip>
              </template>
            </v-select>

            <div class="publish-actions">
              <v-btn 
                type="submit" 
                color="success" 
                size="large"
                :loading="publishing"
                :disabled="publishing"
                prepend-icon="mdi-check"
                class="submit-btn"
              >
                {{ publishing ? '发布中...' : '确认发布' }}
              </v-btn>
              
              <v-btn 
                @click="publishDialog = false"
                variant="outlined"
                size="large"
                :disabled="publishing"
                class="cancel-btn"
              >
                取消
              </v-btn>
            </div>
          </v-form>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- 成功提示对话框 -->
    <v-dialog v-model="successDialog" max-width="400">
      <v-card class="success-card">
        <v-card-text class="text-center pa-6">
          <v-icon color="success" size="64" class="mb-4">mdi-check-circle</v-icon>
          <h3 class="success-title">发布成功！</h3>
          <p class="success-text">实训项目已成功发布到选定班级</p>
          <v-btn 
            color="success" 
            @click="successDialog = false; resetForm()"
            class="mt-4"
          >
            继续创建
          </v-btn>
        </v-card-text>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from 'axios';
import { backendUrl } from '@/main';

export default {
  data() {
    return {
      designContent: '',
      tasks: [],
      contentRules: [
        value => !!value?.trim() || '请输入实训项目描述',
        value => (value && value.length >= 10) || '项目描述至少需要10个字符',
        value => (value && value.length <= 500) || '项目描述不能超过500个字符'
      ],
      nameRules: [
        value => !!value?.trim() || '请输入实训项目名称',
        value => (value && value.length >= 2) || '项目名称至少需要2个字符'
      ],
      classRules: [
        value => (value && value.length > 0) || '请至少选择一个班级'
      ],
      loading: false,
      publishing: false,
      publishDialog: false,
      successDialog: false,
      assignmentName: '',
      selectedClasses: [],
      classes: [],
      panel: [],
      error: ''
    };
  },
  mounted() {
    this.getClasses();
  },
  methods: {
    async getClasses() {
      try {
        const response = await axios.get(`${backendUrl}/getClasses`);
        this.classes = response.data;
      } catch (error) {
        console.error('获取班级列表失败:', error);
        this.error = '获取班级列表失败，请检查网络连接后重试';
      }
    },
    
    async submitForm() {
      if (this.$refs.form.validate()) {
        this.loading = true;
        this.error = '';
        this.tasks = [];

        try {
          const response = await axios.post(`${backendUrl}/generateWork`, {
            content: this.designContent
          });

          console.log('生成任务响应:', response.data);
          
          if (Array.isArray(response.data) && response.data.length > 0) {
            this.tasks = response.data;
            // 自动展开前3个任务
            this.panel = [0, 1, 2].slice(0, this.tasks.length);
          } else {
            this.error = 'AI生成的任务格式异常，请重新尝试';
          }
        } catch (error) {
          console.error('生成任务失败:', error);
          this.error = error.response?.data?.error || 'AI服务暂时不可用，请稍后重试';
        } finally {
          this.loading = false;
        }
      }
    },
    
    publish() {
      this.assignmentName = `${this.designContent.substring(0, 20)}实训项目`;
      this.publishDialog = true;
    },
    
    async submitAssignment() {
      if (this.$refs.publishForm.validate()) {
        this.publishing = true;
        
        const params = {
          creatorTno: localStorage.getItem('username'),
          assignmentName: this.assignmentName,
          tasksJson: JSON.stringify(this.tasks),
          publishDate: new Date().toISOString(),
          selectedClasses: this.selectedClasses
        };

        try {
          const response = await axios.post(`${backendUrl}/createAssignment`, params);
          console.log('实训发布响应:', response.data);
          
          this.publishDialog = false;
          this.successDialog = true;
        } catch (error) {
          console.error('发布失败:', error);
          this.error = error.response?.data?.error || '发布失败，请检查网络连接后重试';
          this.publishing = false;
        } finally {
          this.publishing = false;
        }
      }
    },
    
    resetForm() {
      this.designContent = '';
      this.tasks = [];
      this.assignmentName = '';
      this.selectedClasses = [];
      this.panel = [];
      this.error = '';
      this.$refs.form?.resetValidation();
    }
  }
};
</script>

<style scoped>
.create-work-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem 0;
}

/* 页面头部 */
.page-header {
  margin-bottom: 2rem;
  padding: 0 2rem;
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

.page-title {
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

/* 主容器 */
.main-container {
  max-width: 1200px;
}

/* 表单卡片 */
.form-card {
  border-radius: 16px;
  margin-bottom: 2rem;
}

.form-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
  padding: 1.5rem 2rem;
}

.form-title {
  font-size: 1.3rem;
  font-weight: 600;
}

.form-content {
  padding: 2rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.generate-btn, .publish-btn {
  min-width: 180px;
  height: 48px;
  font-weight: 600;
}

/* 任务section */
.tasks-section {
  margin-top: 2rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding: 0 1rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.tasks-panels {
  border-radius: 12px;
  overflow: hidden;
}

.task-panel {
  margin-bottom: 1rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.task-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.task-number {
  font-weight: 700;
}

.knowledge-point {
  font-weight: 600;
  font-size: 1.1rem;
}

.task-content {
  background: #f8f9fa;
}

.task-description {
  padding: 1rem 0;
}

.task-subtitle {
  color: #333;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.task-text {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid #667eea;
  line-height: 1.6;
  font-size: 1rem;
}

/* 发布对话框 */
.publish-card {
  border-radius: 16px;
}

.publish-header {
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
  padding: 1.5rem 2rem;
}

.publish-title {
  font-size: 1.3rem;
  font-weight: 600;
}

.publish-content {
  padding: 2rem;
}

.publish-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

.submit-btn, .cancel-btn {
  min-width: 120px;
  height: 44px;
}

/* 成功对话框 */
.success-card {
  border-radius: 16px;
  text-align: center;
}

.success-title {
  color: #4CAF50;
  margin-bottom: 0.5rem;
}

.success-text {
  color: #666;
  margin-bottom: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .create-work-container {
    padding: 1rem 0;
  }
  
  .page-header {
    padding: 0 1rem;
  }
  
  .header-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
    padding: 1.5rem;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .form-content {
    padding: 1.5rem;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .generate-btn, .publish-btn {
    width: 100%;
  }
  
  .section-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .publish-actions {
    flex-direction: column;
  }
  
  .submit-btn, .cancel-btn {
    width: 100%;
  }
}

/* 动画效果 */
.form-card, .task-panel {
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
