<template>
  <v-app>
    <v-main>
      <v-container>
        <v-row>
          <v-col cols="12">
            <h1>安理百科</h1>
            <v-card class="dialogue-card" ref="dialogueCard" variant="flat">
              <v-card-text>
                <v-list>
                  <v-list-item
                    v-for="(dialogue, index) in dialogues"
                    :key="index"
                  >
                    <v-list-item-content>
                      <v-card
                        :prepend-icon="
                          dialogue.sender === 'user'
                            ? 'mdi-account'
                            : 'mdi-android'
                        "
                        :class="[
                          'multi-line-chip',
                          dialogue.sender === 'user'
                            ? 'user-message'
                            : 'ai-message',
                        ]"
                        :color="
                          dialogue.sender === 'user'
                            ? 'blue lighten-4'
                            : 'green lighten-4'
                        "
                      >
                        {{ dialogue.text }}
                      </v-card>
                    </v-list-item-content>
                  </v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
            <v-card class="input-card" variant="flat">
              <v-text-field
                v-model="userQuery"
                label="询问关于安理的任何问题...(按下Enter发送)"
                @keydown="handleKeydown"
                ref="messageInput"
                multi-line
                rows="1"
              ></v-text-field>
              <v-btn color="primary" @click="sendQuery">发送</v-btn>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { getCurrentInstance } from "vue";
export default {
  setup() {
    const instance = getCurrentInstance();
    const backendUrl = instance.appContext.config.globalProperties.$backendUrl;
    return {
      backendUrl,
    };
  },
  data() {
    return {
      userQuery: "",
      dialogues: [],
      aiPlaceholderIndex: null,
    };
  },
  methods: {
    handleKeydown(event) {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault(); // 阻止默认的 Enter 行为（换行）
        this.sendQuery(); // 调用发送消息的方法
      }
    },
    async sendQuery() {
      const userText = this.userQuery.trim();
      if (userText) {
        this.dialogues.push({ text: userText, sender: "user" });
        this.userQuery = "";

        const url = `${this.backendUrl}/api/chat`; // 替换为你的 Flask API

        // 添加AI正在处理的占位符
        this.aiPlaceholderIndex = this.dialogues.length;
        this.dialogues.push({ text: "别吵，我在烧烤...", sender: "ai" });

        try {
          const response = await fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ chat: userText }),
          });
          if (!response.body) {
            throw new Error("Failed to get readable stream.");
          }
          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          let aiResponse = "";
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            aiResponse += decoder.decode(value, { stream: true });
          }

          // 更新占位符为实际响应内容
          this.dialogues.splice(this.aiPlaceholderIndex, 1, {
            text: aiResponse,
            sender: "ai",
          });
        } catch (error) {
          console.error("Failed to send query: ", error);
          this.dialogues.splice(this.aiPlaceholderIndex, 1, {
            text: "AI 响应失败.",
            sender: "ai",
          });
        }
      }
    },
  },
};
</script>

<style scoped>
.dialogue-card {
  max-height: 70vh; /* 设置对话卡片的最大高度 */
  overflow-y: auto; /* 使其内容可滚动 */
  margin-bottom: 80px; /* 为输入框留出空间 */
}

.multi-line-chip {
  padding: 10px 15px;
  white-space: normal; /* 允许文本自动换行 */
  line-height: 1.5; /* 调整行高 */
  max-width: 100%; /* 设置最大宽度，根据需要调整 */
  margin-bottom: 8px; /* 为对话间增加间距 */
}

.input-card {
  position: fixed;
  bottom: 0;
  max-width: 80%; /* 设置最大宽度，根据需要调整 */
  width: 100%;
  display: flex;
  align-items: center;
  padding: 16px;

  z-index: 1000; /* 确保它在其他元素之上 */
}

.v-text-field {
  flex-grow: 1;
  margin-right: 16px; /* 为按钮留出空间 */
}
</style>
