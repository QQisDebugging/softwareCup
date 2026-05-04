<template>
  <div class="sql-generate-container">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <v-icon color="primary" size="32" class="mr-3">mdi-database</v-icon>
          <div>
            <h1 class="page-title">SQL语句生成</h1>
            <p class="page-subtitle">根据自然语言描述，智能生成高效的SQL查询语句</p>
          </div>
        </div>
        <div class="stats-section">
          <div class="stat-item">
            <v-icon color="primary">mdi-database-search</v-icon>
            <span>智能查询</span>
          </div>
          <div class="stat-item">
            <v-icon color="info">mdi-table</v-icon>
            <span>表结构解析</span>
          </div>
          <div class="stat-item">
            <v-icon color="success">mdi-code-tags</v-icon>
            <span>SQL生成</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <v-container fluid>
        <v-row>
          <!-- 左侧表结构输入 -->
          <v-col cols="12" md="6">
            <v-card class="schema-card" elevation="8">
              <v-card-title class="schema-header">
                <v-icon color="primary" class="mr-2">mdi-table</v-icon>
                数据库表结构
                <v-spacer></v-spacer>
                <v-chip color="primary" variant="outlined" size="small">
                  <v-icon size="small" class="mr-1">mdi-database</v-icon>
                  SQL Schema
                </v-chip>
              </v-card-title>
              
              <v-card-text class="pa-4">
                <div class="schema-info mb-4">
                  <v-alert
                    type="info"
                    variant="tonal"
                    density="compact"
                    icon="mdi-information"
                    class="mb-4"
                  >
                    请在下方输入您的数据库表结构，包括表名、字段名、字段类型等信息
                  </v-alert>
                </div>
                
                <div class="editor-wrapper">
                  <codemirror 
                    v-model="code" 
                    :extensions="extensions" 
                    @ready="handleReady"
                    placeholder="请输入数据库表结构，例如：&#10;CREATE TABLE users (&#10;  id INT PRIMARY KEY,&#10;  name VARCHAR(50),&#10;  email VARCHAR(100),&#10;  created_at TIMESTAMP&#10;);"
                    class="sql-editor"
                  />
                </div>
                
                <div class="schema-examples mt-4">
                  <v-expansion-panels variant="accordion">
                    <v-expansion-panel>
                      <v-expansion-panel-title>
                        <v-icon class="mr-2">mdi-help-circle</v-icon>
                        查看示例表结构
                      </v-expansion-panel-title>
                      <v-expansion-panel-text>
                        <div class="example-content">
                          <pre class="example-code">CREATE TABLE users (
  id INT PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  email VARCHAR(100) UNIQUE,
  age INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
  id INT PRIMARY KEY,
  user_id INT,
  product_name VARCHAR(100),
  price DECIMAL(10,2),
  order_date DATE,
  FOREIGN KEY (user_id) REFERENCES users(id)
);</pre>
                        </div>
                      </v-expansion-panel-text>
                    </v-expansion-panel>
                  </v-expansion-panels>
                </div>
              </v-card-text>
            </v-card>
          </v-col>

          <!-- 右侧查询生成 -->
          <v-col cols="12" md="6">
            <v-card class="query-card" elevation="8">
              <v-card-title class="query-header">
                <v-icon color="success" class="mr-2">mdi-console</v-icon>
                SQL查询生成
                <v-spacer></v-spacer>
                <v-chip color="success" variant="outlined" size="small">
                  <v-icon size="small" class="mr-1">mdi-auto-fix</v-icon>
                  AI生成
                </v-chip>
              </v-card-title>

              <v-card-text class="pa-4">
                <!-- 查询输入区域 -->
                <div class="query-input-section">
                  <v-textarea
                    id="userQueryInput"
                    v-model="userQuery"
                    label="描述您想要的查询"
                    placeholder="例如：查询年龄大于25岁的用户信息"
                    rows="3"
                    variant="outlined"
                    hide-details
                    class="query-input"
                  />
                  
                  <div class="query-actions mt-3">
                    <v-btn
                      @click="GenerateSql"
                      :disabled="isLoading"
                      :loading="isLoading"
                      color="primary"
                      size="large"
                      class="generate-btn"
                    >
                      <v-icon class="mr-2">mdi-auto-fix</v-icon>
                      {{ isLoading ? '生成中...' : '生成SQL' }}
                    </v-btn>
                    
                    <v-btn
                      @click="clearQuery"
                      variant="outlined"
                      color="secondary"
                      size="large"
                      class="ml-2"
                    >
                      <v-icon class="mr-2">mdi-refresh</v-icon>
                      清空
                    </v-btn>
                  </div>
                </div>

                <!-- 结果展示区域 -->
                <div class="result-section mt-6" v-if="answer || isLoading">
                  <div class="result-header">
                    <v-icon color="success" class="mr-2">mdi-check-circle</v-icon>
                    <span class="result-title">SQL查询结果</span>
                    <v-spacer></v-spacer>
                    <v-btn
                      v-if="answer"
                      @click="copyToClipboard"
                      size="small"
                      variant="text"
                      color="primary"
                    >
                      <v-icon size="16" class="mr-1">mdi-content-copy</v-icon>
                      复制
                    </v-btn>
                  </div>
                  
                  <v-card class="result-card" variant="outlined">
                    <v-card-text v-if="isLoading" class="loading-content">
                      <div class="loading-wrapper">
                        <v-progress-circular
                          indeterminate
                          color="primary"
                          size="24"
                          class="mr-3"
                        />
                        <span>AI正在分析表结构并生成SQL语句...</span>
                      </div>
                    </v-card-text>
                    
                    <v-card-text v-else class="result-content">
                      <div class="markdown-body" v-html="renderedMarkdown"></div>
                    </v-card-text>
                  </v-card>
                </div>

                <!-- 使用提示 -->
                <div class="tips-section mt-6">
                  <v-alert
                    type="success"
                    variant="tonal"
                    density="compact"
                    icon="mdi-lightbulb"
                  >
                    <div class="tips-content">
                      <div class="tips-title">使用提示</div>
                      <div class="tips-list">
                        <div class="tip-item">• 请先输入完整的表结构信息</div>
                        <div class="tip-item">• 用自然语言描述您的查询需求</div>
                        <div class="tip-item">• 支持复杂的多表关联查询</div>
                        <div class="tip-item">• 生成的SQL语句会包含详细说明</div>
                      </div>
                    </div>
                  </v-alert>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, shallowRef, getCurrentInstance, computed } from 'vue';
import { Codemirror } from 'vue-codemirror';
import { sql } from '@codemirror/lang-sql';
import { oneDark } from '@codemirror/theme-one-dark';
import MarkdownIt from 'markdown-it';
import axios from '@/utils/axiosConfig';

export default defineComponent({
  components: {
    Codemirror
  },
  setup() {
    const instance = getCurrentInstance();
    const backendUrl = instance.appContext.config.globalProperties.$backendUrl;

    const code = ref('');
    const userQuery = ref('');
    const answer = ref("");
    const isLoading = ref(false);

    const extensions = [sql(), oneDark];
    const view = shallowRef();
    const md = new MarkdownIt();

    const handleReady = (payload) => {
      view.value = payload.view;
    };

    const renderedMarkdown = computed(() => {
      return md.render(answer.value);
    });

    const GenerateSql = async () => {
      if (!code.value.trim()) {
        alert('请先输入数据库表结构');
        return;
      }
      
      if (!userQuery.value.trim()) {
        alert('请输入查询描述');
        return;
      }

      answer.value = '';
      
      try {
        isLoading.value = true;
        const response = await axios.post(`${backendUrl}/api/sqlgenerate`, {
          table: code.value,
          query: userQuery.value
        });

        const responseData = await response.data;
        console.log(responseData);
        answer.value = responseData.result;
      } catch (error) {
        console.error("Failed to send query: ", error);
        answer.value = "生成失败，请检查表结构和查询描述是否正确。";
      } finally {
        isLoading.value = false;
      }
    };

    const clearQuery = () => {
      userQuery.value = '';
      answer.value = '';
    };

    const copyToClipboard = () => {
      navigator.clipboard.writeText(answer.value).then(() => {
        alert('已复制到剪贴板');
      });
    };

    return {
      code,
      userQuery,
      extensions,
      handleReady,
      answer,
      renderedMarkdown,
      GenerateSql,
      clearQuery,
      copyToClipboard,
      isLoading
    };
  }
});
</script>

<style scoped>
.sql-generate-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
}

.sql-generate-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
  animation: float 20s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

.page-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.title-section {
  display: flex;
  align-items: center;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
}

.page-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 4px 0 0 0;
}

.stats-section {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  color: #475569;
}

.main-content {
  padding: 24px;
  position: relative;
  z-index: 1;
}

.schema-card, .query-card {
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(10px);
  border-radius: 16px !important;
  overflow: hidden;
}

.schema-header, .query-header {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-bottom: 1px solid rgba(226, 232, 240, 0.5);
  font-weight: 600;
  color: #334155;
}

.schema-info {
  background: rgba(248, 250, 252, 0.8);
  border-radius: 8px;
  padding: 12px;
}

.editor-wrapper {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.sql-editor {
  min-height: 300px;
  font-family: 'Fira Code', 'Consolas', monospace;
}

.schema-examples {
  background: rgba(248, 250, 252, 0.5);
  border-radius: 8px;
  padding: 8px;
}

.example-content {
  padding: 8px;
}

.example-code {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.4;
  color: #334155;
  overflow-x: auto;
}

.query-input-section {
  background: rgba(248, 250, 252, 0.8);
  border-radius: 12px;
  padding: 20px;
}

.query-input {
  background: white;
  border-radius: 8px;
}

.query-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.generate-btn {
  border-radius: 12px;
  font-weight: 600;
  text-transform: none;
  padding: 0 24px;
}

.result-section {
  background: rgba(248, 250, 252, 0.8);
  border-radius: 12px;
  padding: 20px;
}

.result-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.result-title {
  font-size: 16px;
  font-weight: 600;
  color: #334155;
}

.result-card {
  background: white !important;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.loading-content {
  padding: 24px;
  text-align: center;
}

.loading-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  font-size: 14px;
}

.result-content {
  padding: 20px;
}

.markdown-body {
  font-size: 14px;
  line-height: 1.6;
  color: #334155;
}

.tips-section {
  background: rgba(248, 250, 252, 0.8);
  border-radius: 12px;
  padding: 16px;
}

.tips-content {
  font-size: 14px;
}

.tips-title {
  font-weight: 600;
  color: #334155;
  margin-bottom: 8px;
}

.tips-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tip-item {
  color: #64748b;
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    text-align: center;
  }
  
  .stats-section {
    justify-content: center;
  }
  
  .query-actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .generate-btn {
    width: 100%;
  }
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}
</style>
