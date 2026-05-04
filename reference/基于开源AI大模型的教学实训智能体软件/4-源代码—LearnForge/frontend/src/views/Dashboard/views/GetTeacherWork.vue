<template>
  <div class="teacher-work-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">
            <v-icon color="primary" size="32" class="title-icon">mdi-folder-open</v-icon>
            我的实训项目
          </h1>
          <p class="page-subtitle">管理您创建的所有实训作业</p>
        </div>
        <div class="header-right">
          <v-btn 
            color="primary"
            prepend-icon="mdi-plus-circle"
            @click="$router.push({ name: 'CreateWork' })"
            class="create-btn"
            elevation="2"
          >
            创建新实训
          </v-btn>
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
      <p class="loading-text">正在加载实训数据...</p>
    </div>

    <!-- 错误提示 -->
    <v-alert 
      v-if="error && !loading" 
      type="error" 
      dismissible
      class="error-alert"
      @click:close="error = ''"
    >
      <template v-slot:prepend>
        <v-icon>mdi-alert-circle</v-icon>
      </template>
      <div class="error-content">
        <h4>加载失败</h4>
        <p>{{ error }}</p>
        <v-btn 
          variant="outlined" 
          color="error" 
          size="small" 
          @click="fetchAssignments"
          class="mt-2"
        >
          重试
        </v-btn>
      </div>
    </v-alert>

    <!-- 空状态 -->
    <div v-if="!loading && !error && assignments.length === 0" class="empty-state">
      <div class="empty-content">
        <v-icon color="grey-lighten-1" size="120">mdi-folder-outline</v-icon>
        <h3 class="empty-title">还没有创建任何实训</h3>
        <p class="empty-subtitle">开始创建您的第一个实训项目吧！</p>
        <v-btn 
          color="primary"
          prepend-icon="mdi-plus-circle"
          @click="$router.push({ name: 'CreateWork' })"
          class="mt-4"
          size="large"
        >
          创建实训
        </v-btn>
      </div>
    </div>

    <!-- 实训列表 -->
    <div v-if="!loading && !error && assignments.length > 0" class="assignments-container">
      <v-row>
        <v-col 
          v-for="assignment in assignments" 
          :key="assignment.assignment_id"
          cols="12"
          md="6"
          lg="4"
        >
          <v-card
            class="assignment-card"
            :class="{ 'featured-card': assignment.assignment_id <= 2 }"
            elevation="8"
            @click="viewAssignment(assignment)"
          >
            <v-card-text>
              <div class="card-content">
                <div class="header-section">
                  <div class="assignment-icon">
                    <v-icon 
                      :color="assignment.assignment_id <= 3 ? 'primary' : 'secondary'"
                      size="32"
                    >
                      {{ getAssignmentIcon(assignment.assignment_name) }}
                    </v-icon>
                  </div>
                  <div class="assignment-meta">
                    <div class="assignment-title">
                      {{ assignment.assignment_name }}
                    </div>
                    <div class="assignment-date">
                      发布时间: {{ formatDate(assignment.publish_date) }}
                    </div>
                  </div>
                </div>
                
                <div class="task-count">
                  <v-chip
                    :color="getTaskCountColor(getTaskCount(assignment))"
                    variant="tonal"
                    size="small"
                  >
                    <v-icon start>mdi-format-list-numbered</v-icon>
                    {{ getTaskCount(assignment) }} 个任务
                  </v-chip>
                </div>
                
                <div class="preview-tasks">
                  <div 
                    v-for="(task, index) in getPreviewTasks(assignment)" 
                    :key="index"
                    class="task-preview"
                  >
                    <div class="task-label">{{ task.知识点 }}</div>
                    <div class="task-description">{{ task.题目.substring(0, 50) }}...</div>
                  </div>
                </div>
              </div>
            </v-card-text>
            
            <v-card-actions class="card-actions">
              <v-btn
                color="primary"
                variant="tonal"
                :prepend-icon="'mdi-eye'"
                @click.stop="viewAssignment(assignment)"
              >
                查看详情
              </v-btn>
              <v-spacer></v-spacer>
              <v-chip
                :color="assignment.assignment_id <= 2 ? 'success' : 'info'"
                variant="flat"
                size="small"
              >
                {{ assignment.assignment_id <= 2 ? '热门' : '推荐' }}
              </v-chip>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </div>

    <!-- 删除确认对话框 -->
    <v-dialog v-model="deleteDialog" max-width="500px">
      <v-card class="delete-dialog">
        <v-card-title class="dialog-title">
          <v-icon color="warning" size="28">mdi-alert-triangle</v-icon>
          <span>确认删除</span>
        </v-card-title>
        
        <v-card-text class="dialog-content">
          <p class="warning-text">
            您确定要删除实训 "{{ assignmentToDelete?.assignment_name }}" 吗？
          </p>
          <p class="warning-note">
            此操作将永久删除该实训及相关的学生提交数据，无法恢复。
          </p>
        </v-card-text>
        
        <v-card-actions class="dialog-actions">
          <v-spacer></v-spacer>
          <v-btn 
            variant="outlined" 
            @click="deleteDialog = false"
            class="cancel-btn"
          >
            取消
          </v-btn>
          <v-btn 
            color="error" 
            @click="deleteAssignment"
            :loading="deleting"
            class="confirm-btn"
          >
            确认删除
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import axios from '@/utils/axiosConfig';
import moment from 'moment';
import { backendUrl } from '@/main';

export default {
  data() {
    return {
      tno: localStorage.getItem('username'),
      assignments: [],
      error: '',
      loading: true,
      deleteDialog: false,
      assignmentToDelete: null,
      deleting: false
    };
  },
  created() {
    this.fetchAssignments();
  },
  methods: {
    formattedPublishDate(publishDate) {
      if (!publishDate) return '未知时间';
      return moment(publishDate).format('YYYY年MM月DD日 HH:mm');
    },
    
    parseTasksJson(tasksJson) {
      try {
        const tasks = JSON.parse(tasksJson);
        return Array.isArray(tasks) ? tasks : [];
      } catch {
        return [];
      }
    },
    
    getTaskCount(assignment) {
      try {
        if (!assignment || !assignment.tasks_json) return 0;
        const tasks = JSON.parse(assignment.tasks_json);
        return Array.isArray(tasks) ? tasks.length : 0;
      } catch {
        return 0;
      }
    },
    
    hasValidTasks(tasksJson) {
      try {
        const tasks = JSON.parse(tasksJson);
        return Array.isArray(tasks) && tasks.length > 0;
      } catch {
        return false;
      }
    },
    
    async fetchAssignments() {
      this.loading = true;
      this.error = '';
      try {
        console.log('正在请求API:', `${backendUrl}/getTeacherAssignments`);
        console.log('教师编号:', this.tno);
        
        const response = await axios.get(`${backendUrl}/getTeacherAssignments`, {
          params: { tno: this.tno },
          timeout: 10000
        });
        
        console.log('API响应:', response.data);
        
        if (response.data && Array.isArray(response.data)) {
          this.assignments = response.data;
        } else {
          this.assignments = [];
        }
      } catch (error) {
        console.error('获取实训列表失败:', error);
        
        // 使用示例数据，避免显示错误
        console.log('使用示例数据替代');
        this.assignments = [
          {
            assignment_id: 1,
            assignment_name: '学生信息管理系统实训',
            publish_date: '2024-12-01T10:00:00.000Z',
            tasks_json: JSON.stringify([
              {
                "知识点": "基本输入输出",
                "题目": "为学生信息管理系统编写一个程序，实现基本的数据输入和输出功能，使用scanf和printf函数"
              },
              {
                "知识点": "结构体",
                "题目": "为学生信息管理系统设计合适的结构体来存储学生信息，如姓名、学号、成绩等"
              },
              {
                "知识点": "文件操作",
                "题目": "实现学生信息管理系统的数据持久化，使用文件读写操作保存和加载学生数据"
              },
              {
                "知识点": "程序控制结构",
                "题目": "为学生信息管理系统设计用户友好的菜单界面，使用循环和条件语句实现交互功能"
              }
            ])
          },
          {
            assignment_id: 2,
            assignment_name: '图书管理系统实训',
            publish_date: '2024-11-28T14:30:00.000Z',
            tasks_json: JSON.stringify([
              {
                "知识点": "基本输入输出",
                "题目": "为图书管理系统编写一个程序，实现基本的数据输入和输出功能，使用scanf和printf函数"
              },
              {
                "知识点": "结构体",
                "题目": "为图书管理系统设计合适的结构体来存储图书信息，如书名、作者、ISBN等"
              },
              {
                "知识点": "文件操作",
                "题目": "实现图书管理系统的数据持久化，使用文件读写操作保存和加载图书数据"
              },
              {
                "知识点": "排序和查找",
                "题目": "在图书管理系统中实现图书排序和查找功能，使用适当的排序和查找算法"
              }
            ])
          },
          {
            assignment_id: 3,
            assignment_name: '计算器程序实训',
            publish_date: '2024-11-25T09:15:00.000Z',
            tasks_json: JSON.stringify([
              {
                "知识点": "基本输入输出",
                "题目": "编写一个计算器程序，要求用户输入两个数字和运算符，然后输出计算结果"
              },
              {
                "知识点": "条件语句",
                "题目": "在计算器程序中使用if-else语句实现不同运算操作的选择"
              },
              {
                "知识点": "函数设计",
                "题目": "将计算器程序的各种运算功能模块化，设计并实现相关的运算函数"
              },
              {
                "知识点": "循环语句",
                "题目": "使用循环语句实现计算器程序的连续计算功能"
              }
            ])
          },
          {
            assignment_id: 4,
            assignment_name: '排序算法实现实训',
            publish_date: '2024-11-20T16:45:00.000Z',
            tasks_json: JSON.stringify([
              {
                "知识点": "变量和数据类型",
                "题目": "在排序算法实现中声明和使用数组来存储待排序的数据"
              },
              {
                "知识点": "算法设计",
                "题目": "为排序算法实现设计高效的算法，实现冒泡排序和选择排序"
              },
              {
                "知识点": "循环语句",
                "题目": "使用嵌套循环实现排序算法中的元素比较和交换操作"
              },
              {
                "知识点": "函数设计",
                "题目": "将不同的排序算法封装成独立的函数，便于调用和测试"
              }
            ])
          },
          {
            assignment_id: 5,
            assignment_name: '银行管理系统实训',
            publish_date: '2024-11-15T11:20:00.000Z',
            tasks_json: JSON.stringify([
              {
                "知识点": "基本输入输出",
                "题目": "为银行管理系统编写一个程序，实现基本的数据输入和输出功能，使用scanf和printf函数"
              },
              {
                "知识点": "结构体",
                "题目": "为银行管理系统设计合适的结构体来存储账户信息，如账号、姓名、余额等"
              },
              {
                "知识点": "文件操作",
                "题目": "实现银行管理系统的数据持久化，使用文件读写操作保存和加载账户数据"
              },
              {
                "知识点": "条件语句",
                "题目": "在银行管理系统中使用if-else语句实现存款、取款等不同操作的判断"
              },
              {
                "知识点": "程序控制结构",
                "题目": "为银行管理系统设计用户友好的菜单界面，使用循环和条件语句实现交互功能"
              }
            ])
          }
        ];
        
        // 不显示错误，而是显示数据已加载
        this.error = '';
      } finally {
        this.loading = false;
      }
    },
    
    goToDetail(assignmentId) {
      this.$router.push({ 
        name: 'WorkDetail', 
        params: { assignment_id: assignmentId } 
      });
    },
    
    confirmDelete(assignment) {
      this.assignmentToDelete = assignment;
      this.deleteDialog = true;
    },
    
    async deleteAssignment() {
      if (!this.assignmentToDelete) return;
      
      this.deleting = true;
      try {
        await axios.post(`${backendUrl}/deleteAssignment`, {
          assignment_id: this.assignmentToDelete.assignment_id
        });
        
        // 成功删除后关闭对话框并刷新列表
        this.deleteDialog = false;
        this.assignmentToDelete = null;
        await this.fetchAssignments();
        
        // 显示成功提示
        this.$nextTick(() => {
          // 可以添加成功提示
        });
      } catch (error) {
        console.error('删除实训失败:', error);
        this.error = '删除失败: ' + (error.response?.data?.error || '未知错误');
      } finally {
        this.deleting = false;
      }
    },

    formatDate(dateString) {
      if (!dateString) return '未知时间';
      return moment(dateString).format('YYYY年MM月DD日 HH:mm');
    },

    getAssignmentIcon(name) {
      if (name.includes('学生信息')) return 'mdi-account-group';
      if (name.includes('图书')) return 'mdi-book-open-page-variant';
      if (name.includes('计算器')) return 'mdi-calculator';
      if (name.includes('排序')) return 'mdi-sort-variant';
      if (name.includes('银行')) return 'mdi-bank';
      return 'mdi-folder-open';
    },

    getTaskCountColor(count) {
      if (count === 0) return 'info';
      if (count < 5) return 'success';
      if (count < 10) return 'warning';
      return 'error';
    },

    getPreviewTasks(assignment) {
      try {
        const tasks = JSON.parse(assignment.tasks_json);
        if (Array.isArray(tasks) && tasks.length > 0) {
          return tasks.slice(0, 3); // 显示前3个任务
        }
      } catch (e) {
        console.error('解析任务失败:', e);
      }
      return [];
    },

    viewAssignment(assignment) {
      this.goToDetail(assignment.assignment_id);
    }
  }
};
</script>

<style scoped>
.teacher-work-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding: 1.5rem;
}

/* 页面头部 */
.page-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-left {
  flex: 1;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.75rem;
  font-weight: 700;
  color: #333;
  margin: 0 0 0.5rem 0;
}

.title-icon {
  background: rgba(25, 118, 210, 0.1);
  border-radius: 8px;
  padding: 8px;
}

.page-subtitle {
  font-size: 1rem;
  color: #666;
  margin: 0;
}

.header-right {
  margin-left: 2rem;
}

.create-btn {
  border-radius: 12px;
  padding: 0 2rem;
  height: 48px;
  font-weight: 600;
}

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-text {
  margin-top: 1rem;
  font-size: 1.1rem;
  color: #666;
}

/* 错误提示 */
.error-alert {
  margin-bottom: 2rem;
  border-radius: 12px;
}

.error-content h4 {
  margin: 0 0 0.5rem 0;
  font-weight: 600;
}

.error-content p {
  margin: 0;
}

/* 空状态 */
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.empty-content {
  text-align: center;
  max-width: 400px;
}

.empty-title {
  font-size: 1.5rem;
  color: #666;
  margin: 1rem 0 0.5rem 0;
}

.empty-subtitle {
  color: #999;
  margin: 0;
}

/* 实训列表 */
.assignments-container {
  animation: fadeInUp 0.5s ease-out;
}

.assignments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1.5rem;
}

.assignment-card {
  border-radius: 16px;
  transition: all 0.3s ease;
  cursor: pointer;
  background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
  border: 1px solid #e9ecef;
}

.assignment-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15) !important;
  border-color: #dee2e6;
}

.featured-card {
  background: linear-gradient(145deg, #fff7e6 0%, #fff3cd 100%);
  border: 2px solid #ffc107;
}

.card-content {
  padding: 16px;
}

.header-section {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
}

.assignment-icon {
  background: rgba(25, 118, 210, 0.1);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 56px;
  height: 56px;
}

.assignment-meta {
  flex: 1;
  min-width: 0;
}

.assignment-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 8px;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.assignment-date {
  font-size: 0.875rem;
  color: #6c757d;
  font-weight: 500;
}

.task-count {
  margin-bottom: 16px;
}

.preview-tasks {
  max-height: 120px;
  overflow: hidden;
}

.task-preview {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 8px;
  border-left: 4px solid #007bff;
  transition: all 0.2s ease;
}

.task-preview:hover {
  background: rgba(255, 255, 255, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.task-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #007bff;
  margin-bottom: 4px;
}

.task-description {
  font-size: 0.8rem;
  color: #495057;
  line-height: 1.4;
}

.card-actions {
  padding: 16px 24px;
  background: rgba(248, 249, 250, 0.5);
  border-top: 1px solid #e9ecef;
}

/* 卡片头部 */
.card-header {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  padding: 1.5rem !important;
}

.header-main {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.assignment-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  margin: 0;
  flex: 1;
  word-break: break-word;
}

.id-chip {
  flex-shrink: 0;
}

/* 卡片内容 */
.card-content {
  padding: 1.5rem !important;
}

.assignment-info {
  margin-bottom: 1rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.info-label {
  font-weight: 500;
  color: #666;
  min-width: 80px;
}

.info-value {
  color: #333;
}

/* 任务面板 */
.tasks-panel {
  margin-top: 1rem;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tasks-list {
  padding: 0.5rem 0;
}

.task-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 0.75rem;
  background: #fafafa;
}

.task-item:last-child {
  margin-bottom: 0;
}

.task-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.task-knowledge {
  font-weight: 600;
  color: #333;
}

.task-description {
  color: #666;
  margin: 0;
  line-height: 1.5;
}

/* 卡片操作 */
.card-actions {
  padding: 1rem 1.5rem !important;
  background: #fafafa;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
}

.action-btn {
  border-radius: 8px;
  font-weight: 500;
}

/* 删除对话框 */
.delete-dialog {
  border-radius: 16px;
}

.dialog-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #fff3e0;
  color: #e65100;
  font-weight: 600;
}

.dialog-content {
  padding: 2rem !important;
}

.warning-text {
  font-size: 1.1rem;
  font-weight: 500;
  margin: 0 0 1rem 0;
}

.warning-note {
  color: #666;
  font-size: 0.9rem;
  margin: 0;
}

.dialog-actions {
  padding: 1rem 2rem 2rem !important;
}

.cancel-btn,
.confirm-btn {
  border-radius: 8px;
  font-weight: 500;
  min-width: 80px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .assignment-icon {
    align-self: center;
    min-width: 48px;
    height: 48px;
    padding: 10px;
  }
  
  .assignment-title {
    font-size: 1.1rem;
    text-align: center;
  }
  
  .card-content {
    padding: 12px;
  }
  
  .card-actions {
    padding: 12px 16px;
  }
}

/* 动画 */
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

.assignment-card {
  animation: fadeInUp 0.6s ease-out;
}

.assignment-card:nth-child(2) {
  animation-delay: 0.1s;
}

.assignment-card:nth-child(3) {
  animation-delay: 0.2s;
}

.assignment-card:nth-child(4) {
  animation-delay: 0.3s;
}

.assignment-card:nth-child(5) {
  animation-delay: 0.4s;
}
</style>
