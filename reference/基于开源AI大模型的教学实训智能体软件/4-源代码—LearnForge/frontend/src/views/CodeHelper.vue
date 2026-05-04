<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from "vue";
// import Markdown from 'vue-markdown';
import { getWebsocketUrl, wsSendMsgFormat } from "./AiChatWebsocket";
import { sparkConfig } from "../config";
import { copyToClipboard, pushRequestTimes } from "@/utils/commonUtil";



// 聊天列表ref

const aiChatListRef = ref(null);

// 会话列表的观察对象（观察子元素变化，用来提示用户体验，当会话有变化时，自动滚动到变化位置）
let chatListObserver;
// 会话列表
let chatList = ref([
  {
    role: "system",
    content:
      "你现在扮演一个资深代码专家，接下来请用富有教育意味的口吻和用户对话。使用markdown格式输出",
  },
]);
// 当前加载回答的index
let loadingIndex = ref(null);

// 连接星火的WebSocket实例
let sparkWS;

// 简单的消息提示函数
const showMessage = (message, type = 'info') => {
  console.log(`[${type.toUpperCase()}]: ${message}`);
  // 可以在这里添加其他的消息提示逻辑
  if (type === 'error') {
    alert(message);
  }
};

// 消息时间戳格式化
const formatTime = (date) => {
  return new Date(date).toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
};

// 欢迎功能列表
const welcomeFeatures = ref([
  '代码调试', '算法解析', '语法检查', '性能优化', '最佳实践'
]);

// 清空对话
const clearChat = () => {
  if (sendBtnDisabled.value) {
    showMessage("正在对话中，无法清空", "warning");
    return;
  }
  
  if (confirm("确定要清空所有对话记录吗？")) {
    chatList.value = [
      {
        role: "system",
        content: "你现在扮演一个资深代码专家，接下来请用富有教育意味的口吻和用户对话。使用markdown格式输出",
      },
    ];
    showMessage("对话已清空", "success");
  }
};

onMounted(() => {
  // 创建 聊天列表 变化的观察者对象
  createMutationObserver(aiChatListRef.value);
  //学习次数++
  pushRequestTimes(1);
});

/**
 * 创建 聊天列表 变化的观察者对象：监听目标元素的高度变化
 * @param targetElement：要观察的目标元素
 */
const createMutationObserver = (targetElement) => {
  chatListObserver = new MutationObserver((mutationsList, observer) => {
    const scrollHeight = targetElement.scrollHeight;

    scrollHandle(scrollHeight);
  });

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

const checkAndSend = (event) => {
  // 检查是否按下了Shift键
  if (!event.shiftKey && event.key === "Enter") {
    event.preventDefault();
    sendQuestion();
  } else {
    // 如果按下了Shift键，则不进行发送，允许换行
    // 注意：这里不需要处理换行符转换，Vue会自动处理
    console.log("换行输入");
  }
};

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
      timestamp: new Date().toISOString(),
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
    // 发送数据
    const sendData = wsSendMsgFormat(sparkConfig, chatList.value);
    sparkWS.send(JSON.stringify(sendData));

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
  console.log("使用HTTP API降级方案");
  
  // 如果没有添加AI响应占位符，添加一个
  if (chatList.value[chatList.value.length - 1].role !== "assistant") {
    chatList.value.push({
      role: "assistant",
      content: "",
      timestamp: new Date().toISOString(),
    });
    loadingIndex.value = chatList.value.length - 1;
  }

  try {
    const url = '/api/ask'; // 使用百度AI API
    const userMessage = chatList.value
      .filter(msg => msg.role !== "system")
      .map(msg => `${msg.role}: ${msg.content}`)
      .join('\n');

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        query: `你现在扮演一个资深代码专家，接下来请用富有教育意味的口吻和用户对话。使用markdown格式输出。\n\n对话历史：\n${userMessage}` 
      })
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
      // 如果不是是最后一条重新回答,则后面重新添加问题继续进行询问
      // 有可能上一条回答内容被直接删除，所以需要循环往前找最近的一条问题记录。找到之后则以这条问题记录为准回答
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
const handleCopyCodeSuccess = () => {
  showMessage("复制成功", "success");
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
  <link
    rel="stylesheet"
    href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/4.0.0/github-markdown.min.css"
  />
  <v-container fluid class="pa-0">
    <div class="ai-chat-view">
      <!-- 头部工具栏 -->
      <v-app-bar flat class="chat-header" color="primary" dark>
        <v-toolbar-title class="text-h6">
          <v-icon class="mr-2">mdi-robot</v-icon>
          AI代码助手
        </v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn 
          icon 
          @click="clearChat" 
          :disabled="sendBtnDisabled"
          title="清空对话"
        >
          <v-icon>mdi-delete-sweep</v-icon>
        </v-btn>
      </v-app-bar>

      <div class="chat-content">
        <ul ref="aiChatListRef" class="ai-chat-list">
          <!-- 欢迎消息 -->
          <li class="ai-chat-item welcome-item">
            <div class="ai-chat-avatar">
              <v-avatar
                :size="50"
                color="primary"
              >
                <v-icon color="white" size="30">mdi-robot</v-icon>
              </v-avatar>
            </div>

            <div class="ai-chat-content-box welcome-box">
              <div class="welcome-title">
                <v-icon class="mr-2" color="primary">mdi-waving-hand</v-icon>
                你好！我是AI代码助手
              </div>
              <div class="welcome-text">
                <v-chip 
                  v-for="feature in welcomeFeatures" 
                  :key="feature" 
                  class="ma-1 feature-chip" 
                  small 
                  color="white"
                  text-color="primary"
                  elevation="2"
                >
                  <v-icon small class="mr-1">mdi-code-tags</v-icon>
                  {{ feature }}
                </v-chip>
              </div>
              <div class="welcome-hint">你可以问我各种代码问题，我会详细解答 💡</div>
            </div>
          </li>
          <!-- 对话消息 -->
          <li
            v-for="(item, index) of chatList"
            class="ai-chat-item"
            :class="item.role + '-item'"
            :key="index"
          >
            <div class="ai-chat-avatar">
              <v-avatar v-if="item.role === 'user'" size="45" color="indigo">
                <v-icon color="white">mdi-account</v-icon>
              </v-avatar>
              <v-avatar v-if="item.role === 'assistant'" size="45" color="primary">
                <v-icon color="white">mdi-robot</v-icon>
              </v-avatar>
            </div>

            <div class="message-content-wrapper">
              <!-- 用户消息 -->
              <div
                v-if="item.role === 'user'"
                class="user-chat-content-box"
              >
                <div class="message-text">{{ item.content }}</div>
                <div class="message-time" v-if="item.timestamp">
                  {{ formatTime(item.timestamp) }}
                </div>
              </div>

              <!-- AI消息 -->
              <div v-if="item.role === 'assistant'" class="ai-chat-content-box">
                <!-- 加载状态 -->
                <div v-if="loadingIndex === index && !item.content" class="loading-container">
                  <v-progress-circular
                    indeterminate
                    color="primary"
                    size="20"
                    width="2"
                  ></v-progress-circular>
                  <span class="loading-text ml-2">AI正在思考中...</span>
                </div>
                
                <!-- AI回复内容 -->
                <div v-if="item.content">
                  <v-md-preview :text="item.content"></v-md-preview>
                  <div class="message-time" v-if="item.timestamp">
                    {{ formatTime(item.timestamp) }}
                  </div>
                </div>

                <!-- 操作按钮 -->
                <div class="ai-chat-operate" v-if="item.content">
                  <v-btn
                    small
                    text
                    color="primary"
                    v-if="!sendBtnDisabled"
                    @click="reReply(index)"
                  >
                    <v-icon small class="mr-1">mdi-refresh</v-icon>
                    重新回答
                  </v-btn>
                  
                  <v-spacer></v-spacer>
                  
                  <v-btn
                    small
                    icon
                    color="grey"
                    @click="copyRecord(item, index)"
                    title="复制内容"
                  >
                    <v-icon small>mdi-content-copy</v-icon>
                  </v-btn>
                  
                  <v-btn
                    small
                    icon
                    color="error"
                    @click="deleteRecord(index)"
                    :disabled="sendBtnDisabled"
                    title="删除消息"
                  >
                    <v-icon small>mdi-delete</v-icon>
                  </v-btn>
                </div>
              </div>
            </div>
          </li>
        </ul>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <v-card flat class="input-card">
          <v-card-text class="pb-2">
            <v-row no-gutters align="center">
              <v-col>
                <v-textarea
                  v-model="problemText"
                  class="chat-input"
                  :maxlength="maxCharCount"
                  placeholder="输入问题，按Enter键发送，Shift+Enter换行..."
                  rows="1"
                  auto-grow
                  outlined
                  dense
                  hide-details
                  @keyup.enter.native="checkAndSend"
                  :disabled="sendBtnDisabled"
                />
              </v-col>
              <v-col cols="auto" class="ml-3">
                <v-btn
                  :disabled="sendBtnDisabled || !problemText.trim()"
                  color="primary"
                  @click="sendQuestion"
                  fab
                  small
                  elevation="2"
                >
                  <v-icon v-if="!sendBtnDisabled">mdi-send</v-icon>
                  <v-progress-circular
                    v-else
                    indeterminate
                    size="20"
                    width="2"
                    color="white"
                  ></v-progress-circular>
                </v-btn>
              </v-col>
            </v-row>
            
            <!-- 字数统计 -->
            <v-row no-gutters class="mt-1">
              <v-col>
                <div class="text-caption text-right" :class="problemText.length > maxCharCount * 0.8 ? 'text-warning' : 'text-grey'">
                  {{ problemText.length }} / {{ maxCharCount }}
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </div>
    </div>
  </v-container>
</template>

<style scoped>
.ai-chat-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  position: relative;
}

.ai-chat-view::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    radial-gradient(circle at 20% 30%, rgba(102, 126, 234, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 70%, rgba(118, 75, 162, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 80%, rgba(102, 126, 234, 0.05) 0%, transparent 50%);
  pointer-events: none;
}

.chat-header {
  flex-shrink: 0;
  border-bottom: 1px solid rgba(102, 126, 234, 0.2);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  box-shadow: 0 2px 12px rgba(102, 126, 234, 0.3);
  z-index: 10;
  position: relative;
}

.chat-header .v-toolbar-title {
  font-weight: 700;
  font-size: 18px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.ai-chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  margin: 0;
  list-style: none;
  scroll-behavior: smooth;
  background: transparent;
}

.ai-chat-item {
  display: flex;
  margin-bottom: 28px;
  align-items: flex-start;
  animation: slideIn 0.4s ease-out;
}

.ai-chat-avatar {
  margin-right: 12px;
  flex-shrink: 0;
}

.ai-chat-avatar .v-avatar {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.message-content-wrapper {
  flex: 1;
  max-width: calc(100% - 60px);
}

/* 欢迎消息样式 */
.welcome-item .ai-chat-content-box {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.welcome-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.welcome-text {
  margin: 16px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.feature-chip {
  background: rgba(255, 255, 255, 0.95) !important;
  color: #667eea !important;
  font-weight: 600 !important;
  border: 2px solid rgba(255, 255, 255, 0.3) !important;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  cursor: pointer;
}

.feature-chip:hover {
  background: rgba(255, 255, 255, 1) !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.feature-chip .v-icon {
  color: #667eea !important;
}

.welcome-hint {
  margin-top: 16px;
  opacity: 0.95;
  font-size: 15px;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* 用户消息样式 */
.user-item {
  flex-direction: row-reverse;
}

.user-item .ai-chat-avatar {
  margin-left: 12px;
  margin-right: 0;
}

.user-chat-content-box {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 20px 20px 8px 20px;
  padding: 14px 18px;
  max-width: 70%;
  margin-left: auto;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.user-chat-content-box .message-text {
  word-wrap: break-word;
  line-height: 1.5;
  font-weight: 500;
}

/* AI消息样式 */
.ai-chat-content-box {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px 20px 20px 8px;
  padding: 18px;
  max-width: 85%;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
}

/* 加载状态 */
.loading-container {
  display: flex;
  align-items: center;
  padding: 12px 0;
  color: #667eea;
}

.loading-text {
  font-size: 14px;
  font-weight: 600;
}

/* 消息时间 */
.message-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 6px;
  text-align: right;
  font-weight: 500;
}

.ai-chat-content-box .message-time {
  color: rgba(0, 0, 0, 0.6);
  text-align: left;
}

/* 操作按钮 */
.ai-chat-operate {
  display: flex;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(102, 126, 234, 0.1);
}

/* 输入区域 */
.input-area {
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(102, 126, 234, 0.2);
}

.input-card {
  background: transparent !important;
}

.chat-input {
  font-size: 16px;
}

.chat-input ::v-deep(.v-field__outline) {
  border-radius: 24px;
  border-color: rgba(102, 126, 234, 0.3);
}

.chat-input ::v-deep(.v-field__input) {
  padding: 14px 20px;
}

.chat-input ::v-deep(.v-field--focused .v-field__outline) {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ai-chat-list {
    padding: 16px;
  }
  
  .ai-chat-item {
    margin-bottom: 20px;
  }
  
  .user-chat-content-box,
  .ai-chat-content-box {
    max-width: 95%;
  }
  
  .ai-chat-avatar {
    margin-right: 8px;
  }
  
  .user-item .ai-chat-avatar {
    margin-left: 8px;
    margin-right: 0;
  }
  
  .welcome-title {
    font-size: 18px;
  }
  
  .feature-chip {
    font-size: 12px;
  }
}

/* 滚动条样式 */
.ai-chat-list::-webkit-scrollbar {
  width: 8px;
}

.ai-chat-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.ai-chat-list::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.ai-chat-list::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
}

/* 动画效果 */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 输入框获得焦点时的特效 */
.chat-input:focus-within {
  animation: fadeIn 0.3s ease;
}

/* 发送按钮样式优化 */
.input-area .v-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
}

.input-area .v-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5);
}

.input-area .v-btn:disabled {
  background: rgba(158, 158, 158, 0.3) !important;
  transform: none;
  box-shadow: none;
}

/* 字数统计样式 */
.text-caption {
  font-weight: 500;
  transition: color 0.3s ease;
}

.text-warning {
  color: #ff6b6b !important;
  font-weight: 600;
}

/* 操作按钮样式优化 */
.ai-chat-operate .v-btn {
  transition: all 0.3s ease;
}

.ai-chat-operate .v-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* 头部按钮样式 */
.chat-header .v-btn {
  transition: all 0.3s ease;
}

.chat-header .v-btn:hover {
  transform: scale(1.05);
  background: rgba(255, 255, 255, 0.1) !important;
}

/* Markdown内容样式优化 */
.ai-chat-content-box ::v-deep(.v-md-preview) {
  background: transparent;
  padding: 0;
}

.ai-chat-content-box ::v-deep(.v-md-preview-wrapper) {
  padding: 0;
}

/* 原有的代码增强样式 */
.markdown-body {
  overflow-y: auto;
}

pre .enhance {
  display: flex;
  color: #fff;
  padding: 0px 10px;
  border-radius: 5px 5px 0 0;
  font-size: 14px;
  background: #404134de;
  justify-content: space-between;

  .copyCode {
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.5s ease-in-out;

    &:hover {
      color: #bae9a4d7;
    }

    i {
      font-size: 16px;
      margin-left: 5px;
    }
  }
}
</style>

