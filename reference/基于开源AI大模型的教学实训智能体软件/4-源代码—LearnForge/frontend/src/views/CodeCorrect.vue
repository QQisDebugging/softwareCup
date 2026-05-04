<script setup>
import { ref, onMounted, onBeforeUnmount, computed, reactive, watch } from "vue";
import { Codemirror } from 'vue-codemirror';
// 语言部分
import { javascript } from '@codemirror/lang-javascript';
import { python } from '@codemirror/lang-python';
import { cpp } from '@codemirror/lang-cpp';
import { java } from '@codemirror/lang-java';
import { sql } from '@codemirror/lang-sql';
import { verilog } from 'codemirror-lang-verilog';
import { oneDark } from '@codemirror/theme-one-dark';
import {
  getWebsocketUrl,
  wsSendMsgFormat,
} from "./AiChatWebsocket";
import { sparkConfig } from "../config";
import { copyToClipboard,pushRequestTimes } from "@/utils/commonUtil";





const languages = ['Java', 'Python', 'JavaScript', "C", "Verilog", "SQL"];
const selectedLanguage = ref("Python");
const languageModes = {
  Java: [java()],  
  Python: [python()],
  JavaScript: [javascript()],
  C: [cpp()],
  Verilog: [verilog()],
  SQL: [sql()]
};
const currentExtensions = computed(() => {
  return (languageModes[selectedLanguage.value] || []).concat(oneDark);
});



// 聊天列表ref
const aiChatListRef = ref(null);

// 会话列表的观察对象（观察子元素变化，用来提示用户体验，当会话有变化时，自动滚动到变化位置）
let chatListObserver;
// 会话列表

const code = ref('print(123)');
let chatList = ref([{ "role": "system", "content": "你现在扮演一个资深代码助手,接下来请用富有教育意义的口吻和用户对话。" }]);


// 当前加载回答的index
let loadingIndex = ref(null);

// 连接星火的WebSocket实例
let sparkWS;

// 简单的消息提示函数
const showMessage = (message, type = 'info') => {
  console.log(`[${type.toUpperCase()}]: ${message}`);
  if (type === 'error') {
    alert(message);
  }
};

onMounted(() => {
  // 创建 聊天列表 变化的观察者对象
  createMutationObserver(aiChatListRef.value);
    //学习次数++
    pushRequestTimes(1)
});

/**
 * 创建 聊天列表 变化的观察者对象：监听目标元素的高度变化
 * @param targetElement：要观察的目标元素
 */
const createMutationObserver = (targetElement) => {
  // 创建一个新的 MutationObserver 实例
  chatListObserver = new MutationObserver((mutationsList, observer) => {
    // 当子元素发生变化时，获取元素的滚动区域高度
    const scrollHeight = targetElement.scrollHeight;
    // 滚动的处理
    scrollHandle(scrollHeight);
  });

  // 启动观察器并配置所需的观察选项
  chatListObserver.observe(targetElement, { childList: true, subtree: true });
};

/**
 * 滚动定位处理
 * @param val
 */
const scrollHandle = (val) => {
  aiChatListRef.value?.scrollTo({
    top: val,
    behavior: "smooth", // 表示滚动行为，支持参数 smooth(平滑滚动),instant(瞬间滚动),默认值 auto
  });
};

// 提问文字
let problemText = ref("");
// 提问最大字数
const maxCharCount = ref(2000);

/**
 * 监听提问文字
 */
const problemTextWatcher = watch(
  () => problemText.value,
  () => {
    // 限制最大字数
    if (problemText.value.length > maxCharCount.value) {
      problemText.value = problemText.value.slice(0, maxCharCount.value);
    }
  }
);

// 发送按钮的禁用状态
const sendBtnDisabled = ref(false);
// webSocket 响应数据状态
let wsMsgReceiveStatus = ref();

const sendQuestion = () => {
  if (sendBtnDisabled.value) {
    // 发送按钮禁用状态
    return;
  }

  if (problemText.value?.trim()?.length <= 0) {
    // 输入问题文字是空字符串
    showMessage("请输入您想了解的内容...", "warning");
    return;
  }

  // 不是在接收消息的时候才可以发送问题
  if (wsMsgReceiveStatus.value !== "receiveIng") {
    chatList.value.push({
      role: "user",
      content: problemText.value,
    });
    
    // 立即清空文本框并禁用发送按钮
    problemText.value = "";
    sendBtnDisabled.value = true;
    wsMsgReceiveStatus.value = "receiveIng";
    
    // 直接使用百度AI，跳过讯飞星火WebSocket
    console.log("直接使用百度AI，跳过讯飞星火WebSocket");
    fallbackToHttpApi();
    
    // 如果想要使用讯飞星火，可以取消注释下面这行，注释掉上面的fallbackToHttpApi()
    // askSpark();
  }
};

/**
 * 连接星火WebSocket并发送问题
 * @param question
 */
const askSpark = () => {
  // 1. 生成鉴权URL
  let wsUrl = getWebsocketUrl(sparkConfig);

  // 2. 判断浏览器是否支持WebSocket
  if ("WebSocket" in window) {
    sparkWS = new WebSocket(wsUrl);
  } else {
    showMessage("浏览器不支持WebSocket", "error");
    resetState();
    return;
  }

  // 3. WebSocket事件监听
  // 3.1 WebSocket连接成功
  sparkWS.onopen = () => {
    chatList.value[0] = {
      role: "system",
      content: "用户给的代码如下：" + code.value + "，你现在扮演一个资深代码助手，接下来请用富有教育意义的口吻和用户对话,先指出代码包含的知识点，使用markdown格式输出",
    };

    const sendData = wsSendMsgFormat(sparkConfig, chatList.value);
    sparkWS.send(JSON.stringify(sendData));
    console.log(chatList.value);
    chatList.value.push({
      role: "assistant",
      content: "",
    });
    loadingIndex.value = chatList.value.length - 1;
  };

  // 3.2 WebSocket监听消息
  sparkWS.onmessage = (res) => {
    // 响应数据
    let resObj = JSON.parse(res.data);

    if (resObj.header.code !== 0) {
      console.error(
        `提问失败:${resObj.header.code} - ${resObj.header.message}`
      );
      sparkWS.close();
      
      // 如果是认证失败或其他WebSocket错误，自动降级到HTTP API
      console.log("WebSocket认证失败，自动降级到HTTP API");
      fallbackToHttpApi();
    } else {
      // 处理响应回来的数据
      wsMsgReceiveHandle(resObj);
    }
  };

  // 3.3 WebSocket连接失败
  sparkWS.onerror = (error) => {
    console.error(`WebSocket连接失败,连接url:${wsUrl}`);
    // 降级到HTTP API
    fallbackToHttpApi();
  };

  // 3.4  WebSocket连接关闭
  sparkWS.onclose = (event) => {
    if (event.code !== 1000 && wsMsgReceiveStatus.value !== "receiveFinshed") {
      console.log("WebSocket意外关闭，尝试HTTP API降级");
      fallbackToHttpApi();
    }
  };
};

/**
 * 处理WebSocket响应回来的数据
 * @param res
 */
const wsMsgReceiveHandle = (res) => {
  console.log(res.payload.choices);
  
  let dataArray = res?.payload?.choices?.text || [];
    for (let i = 0; i < dataArray.length; i++) {
      chatList.value[chatList.value.length - 1].content += dataArray[i].content;
    }

  // 继续接收消息
  if (res.payload.choices.status === 1 || res.payload.choices.status === 0) {
    wsMsgReceiveStatus.value = "receiveIng";
  }

  // 完成接收消息
  if (res.payload.choices.status === 2) {
    wsMsgReceiveStatus.value = "receiveFinshed";
    loadingIndex.value = null;
    sendBtnDisabled.value = false;
    sparkWS.close();
  }
};

/**
 * HTTP API降级方案
 */
const fallbackToHttpApi = async () => {
  console.log("使用HTTP API降级方案进行代码纠错");
  
  // 如果没有添加AI响应占位符，添加一个
  if (chatList.value[chatList.value.length - 1].role !== "assistant") {
    chatList.value.push({
      role: "assistant",
      content: "",
    });
    loadingIndex.value = chatList.value.length - 1;
  }

  try {
    const url = '/api/ask'; // 使用百度AI API
    const codeContent = code.value;
    const language = selectedLanguage.value;
    
    // 获取最后一个用户消息
    const lastUserMessage = chatList.value
      .filter(msg => msg.role === "user")
      .slice(-1)[0]?.content || "";

    let query = `你是一个资深的代码专家，请帮我检查以下${language}代码中的错误并提供修改建议：\n\n\`\`\`${language}\n${codeContent}\n\`\`\`\n\n请指出代码中的问题、错误原因，并提供正确的代码示例。使用markdown格式输出。`;
    
    // 如果有用户问题，添加到查询中
    if (lastUserMessage) {
      query += `\n\n用户问题：${lastUserMessage}`;
    }

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });

    if (!response.body) {
      throw new Error('Failed to get readable stream.');
    }

    const reader = response.body.getReader();
    wsMsgReceiveStatus.value = "receiveIng";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = new TextDecoder().decode(value);
      chatList.value[chatList.value.length - 1].content += chunk;
    }

    // 完成接收
    wsMsgReceiveStatus.value = "receiveFinshed";
    loadingIndex.value = null;
    sendBtnDisabled.value = false;

  } catch (error) {
    console.error('HTTP API降级也失败:', error);
    chatList.value[chatList.value.length - 1].content = "抱歉，AI服务暂时不可用，请稍后再试。";
    
    resetState();
  }
};

/**
 * 重置状态
 */
const resetState = () => {
  loadingIndex.value = null;
  sendBtnDisabled.value = false;
  wsMsgReceiveStatus.value = "receiveFinshed";
};

/**
 * 拷贝会话记录到剪贴板
 * @param item
 * @param index
 */
const copyRecord = (item, index) => {
  const content = item.content;
  copyToClipboard({
    content,
    success() {
      showMessage("复制成功", "success");
    },
    error() {
      showMessage("复制失败", "error");
    },
  });
};



/**
 * 删除记录
 * @param index
 */
const deleteRecord = (index) => {
  if (!sendBtnDisabled.value) {
    chatList.value.splice(index, 1);
  }
};

/**
 * 重新回答
 * @param index
 */
const reReply = (index) => {
  if (wsMsgReceiveStatus.value !== "receiveIng") {
    if (chatList.value.length - 1 === index) {
      // 如果是最后一条重新回答,则直接删除最后一条记录重新作答
      deleteRecord(index);
      sendBtnDisabled.value = true;
      askSpark();
    } else {
      let i = index - 1;
      while (i >= 0) {
        if (chatList.value[i].role === "user" && chatList.value[i].content) {
          // 符合条件：角色是用户，有问题内容
          chatList.value.push({
            role: "user",
            content: chatList.value[index - 1].content,
          });
          sendBtnDisabled.value = true;
          askSpark();
          break;
        }
        i--;
      }
    }
  }
};

/**
 * AI回答内容中代码块的复制
 */
const handleCopyCodeSuccess = (code) => {
  copyToClipboard({
    content: code,
    success() {
      showMessage("复制成功", "success");
    },
    error() {
      showMessage("复制失败", "error");
    },
  });
};

/**
 * 组件销毁时
 */
onBeforeUnmount(() => {
  // 停止属性监听
  problemTextWatcher();
  // 停止对会话列表的观察变动
  chatListObserver.disconnect();
});
</script>
<template>
  <div class="code-correct-container">
    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="header-content">
        <div class="title-section">
          <v-icon color="primary" size="32" class="mr-3">mdi-bug-check</v-icon>
          <div>
            <h1 class="page-title">代码纠错助手</h1>
            <p class="page-subtitle">AI智能检测代码错误，提供修复建议</p>
          </div>
        </div>
        <div class="stats-section">
          <div class="stat-item">
            <v-icon color="success">mdi-check-circle</v-icon>
            <span>智能分析</span>
          </div>
          <div class="stat-item">
            <v-icon color="warning">mdi-alert-circle</v-icon>
            <span>错误检测</span>
          </div>
          <div class="stat-item">
            <v-icon color="info">mdi-lightbulb</v-icon>
            <span>优化建议</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <v-container fluid>
        <v-row>
          <!-- 左侧代码编辑器 -->
          <v-col cols="12" md="6">
            <v-card class="editor-card" elevation="8">
              <v-card-title class="editor-header">
                <v-icon color="primary" class="mr-2">mdi-code-tags</v-icon>
                代码编辑器
                <v-spacer></v-spacer>
                <v-chip color="primary" variant="outlined" size="small">
                  {{ selectedLanguage }}
                </v-chip>
              </v-card-title>
              
              <v-card-text class="pa-4">
                <div class="language-selector mb-4">
                  <v-select
                    v-model="selectedLanguage"
                    :items="languages"
                    label="选择编程语言"
                    variant="outlined"
                    density="comfortable"
                    prepend-inner-icon="mdi-code-braces"
                    hide-details
                  />
                </div>
                
                <div class="editor-wrapper">
                  <codemirror 
                    v-model="code" 
                    :extensions="currentExtensions" 
                    @ready="handleReady"
                    class="code-editor"
                  />
                </div>
              </v-card-text>
            </v-card>
          </v-col>

          <!-- 右侧AI对话区域 -->
          <v-col cols="12" md="6">
            <v-card class="chat-card" elevation="8">
              <v-card-title class="chat-header">
                <v-icon color="success" class="mr-2">mdi-robot</v-icon>
                AI助手对话
                <v-spacer></v-spacer>
                <v-chip color="success" variant="outlined" size="small">
                  <v-icon size="small" class="mr-1">mdi-circle</v-icon>
                  在线
                </v-chip>
              </v-card-title>

              <v-card-text class="pa-0">
                <div class="chat-container">
                  <!-- 聊天列表 -->
                  <div ref="aiChatListRef" class="chat-list">
                    <!-- 欢迎消息 -->
                    <div class="welcome-message">
                      <v-avatar size="40" class="mr-3">
                        <v-img src="https://ydcqoss.ydcode.cn/static/officialhome/ydyx_avatar.png" />
                      </v-avatar>
                      <div class="welcome-content">
                        <div class="welcome-title">你好！我是AI代码助手</div>
                        <div class="welcome-text">我可以帮助您：</div>
                        <div class="feature-list">
                          <div class="feature-item">
                            <v-icon size="16" color="success">mdi-check</v-icon>
                            检测代码错误
                          </div>
                          <div class="feature-item">
                            <v-icon size="16" color="success">mdi-check</v-icon>
                            分析问题原因
                          </div>
                          <div class="feature-item">
                            <v-icon size="16" color="success">mdi-check</v-icon>
                            提供修复建议
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- 对话消息 -->
                    <div 
                      v-for="(item, index) in chatList.slice(1)" 
                      :key="index"
                      class="message-item"
                      :class="item.role + '-message'"
                    >
                      <div class="message-avatar">
                        <v-avatar size="36" :color="item.role === 'user' ? 'primary' : 'success'">
                          <v-icon :color="item.role === 'user' ? 'white' : 'white'">
                            {{ item.role === 'user' ? 'mdi-account' : 'mdi-robot' }}
                          </v-icon>
                        </v-avatar>
                      </div>
                      
                      <div class="message-content">
                        <div v-if="item.role === 'user'" class="user-message">
                          {{ item.content }}
                        </div>
                        <div v-else class="assistant-message">
                          <v-md-preview :text="item.content" class="markdown-preview" />
                          <div class="message-actions">
                            <v-btn
                              v-if="!sendBtnDisabled"
                              size="small"
                              variant="text"
                              color="primary"
                              @click="reReply(index + 1)"
                            >
                              <v-icon size="16" class="mr-1">mdi-refresh</v-icon>
                              重新回答
                            </v-btn>
                            <v-btn
                              size="small"
                              variant="text"
                              color="error"
                              @click="deleteRecord(index + 1)"
                            >
                              <v-icon size="16" class="mr-1">mdi-delete</v-icon>
                              删除
                            </v-btn>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- 加载状态 -->
                    <div v-if="loadingIndex !== null" class="loading-message">
                      <v-avatar size="36" color="success">
                        <v-icon color="white">mdi-robot</v-icon>
                      </v-avatar>
                      <div class="loading-content">
                        <v-progress-circular
                          indeterminate
                          color="primary"
                          size="20"
                          class="mr-2"
                        />
                        AI正在分析中...
                      </div>
                    </div>
                  </div>

                  <!-- 输入区域 -->
                  <div class="input-area">
                    <div class="input-container">
                      <v-textarea
                        v-model="problemText"
                        :maxlength="maxCharCount"
                        variant="outlined"
                        label="描述您的问题或直接点击发送分析代码"
                        rows="2"
                        auto-grow
                        hide-details
                        @keyup.enter.exact="sendQuestion"
                        @keyup.enter.shift.exact.prevent
                        class="message-input"
                      />
                      <div class="input-actions">
                        <v-btn
                          :disabled="sendBtnDisabled"
                          :loading="sendBtnDisabled"
                          color="primary"
                          size="large"
                          @click="sendQuestion"
                          class="send-button"
                        >
                          <v-icon class="mr-2">mdi-send</v-icon>
                          {{ sendBtnDisabled ? '分析中...' : '发送' }}
                        </v-btn>
                      </div>
                    </div>
                    <div class="input-hint">
                      <span class="text-caption">{{ problemText.length }}/{{ maxCharCount }}</span>
                      <span class="text-caption ml-2">按Enter发送，Shift+Enter换行</span>
                    </div>
                  </div>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </div>
  </div>
</template>


<style scoped>
.code-correct-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
}

.code-correct-container::before {
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

.editor-card, .chat-card {
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(10px);
  border-radius: 16px !important;
  overflow: hidden;
}

.editor-header, .chat-header {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-bottom: 1px solid rgba(226, 232, 240, 0.5);
  font-weight: 600;
  color: #334155;
}

.language-selector {
  background: rgba(248, 250, 252, 0.8);
  border-radius: 8px;
  padding: 12px;
}

.editor-wrapper {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.code-editor {
  min-height: 400px;
  font-family: 'Fira Code', 'Consolas', monospace;
}

.chat-container {
  height: 600px;
  display: flex;
  flex-direction: column;
}

.chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  scroll-behavior: smooth;
}

.welcome-message {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 12px;
  margin-bottom: 16px;
}

.welcome-content {
  flex: 1;
}

.welcome-title {
  font-size: 18px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 8px;
}

.welcome-text {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 12px;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #475569;
}

.message-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.user-message .message-content {
  margin-left: auto;
}

.message-content {
  flex: 1;
  max-width: 80%;
}

.user-message .message-content {
  max-width: 70%;
}

.user-message {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  padding: 12px 16px;
  border-radius: 18px 18px 4px 18px;
  font-size: 14px;
  line-height: 1.5;
}

.assistant-message {
  background: #f8fafc;
  border-radius: 18px 18px 18px 4px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.markdown-preview {
  padding: 16px;
  font-size: 14px;
  line-height: 1.6;
}

.message-actions {
  display: flex;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(248, 250, 252, 0.8);
  border-top: 1px solid #e2e8f0;
}

.loading-message {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 12px;
  margin-bottom: 16px;
}

.loading-content {
  display: flex;
  align-items: center;
  color: #3b82f6;
  font-size: 14px;
  font-weight: 500;
}

.input-area {
  padding: 16px;
  background: rgba(248, 250, 252, 0.8);
  border-top: 1px solid #e2e8f0;
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
}

.send-button {
  border-radius: 12px;
  font-weight: 600;
  text-transform: none;
  padding: 0 20px;
}

.input-hint {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
  color: #64748b;
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
  
  .chat-container {
    height: 500px;
  }
  
  .message-content {
    max-width: 90%;
  }
  
  .input-container {
    flex-direction: column;
    gap: 8px;
  }
}

/* 滚动条样式 */
.chat-list::-webkit-scrollbar {
  width: 6px;
}

.chat-list::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.chat-list::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 3px;
}

.chat-list::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.3);
}
</style>