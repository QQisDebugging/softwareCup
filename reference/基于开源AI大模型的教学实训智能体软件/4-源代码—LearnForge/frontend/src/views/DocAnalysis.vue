<template>
  <link
    rel="stylesheet"
    href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/4.0.0/github-markdown.min.css"
  />

  <v-app>
    <v-container>
      <v-row>
        <v-col cols="8">
          <v-card class="pa-3">
            <v-card-text>
              <div class="markdown-body" v-html="renderedMarkdown"></div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="4">
          <v-card class="pa-3">
            <v-file-input
              v-model="file"
              label="选择文件"
              accept=".pdf, .docx"
              @change="uploadFile"
            ></v-file-input>
            <v-alert v-if="uploadStatus" :value="true" type="success">{{
              uploadStatus
            }}</v-alert>
          </v-card>
        </v-col>
      </v-row>

      <v-row class="input-row">
        <v-col cols="12">
          <v-card class="pa-3">
            <v-text-field
              v-model="messageInput"
              label="输入信息"
            ></v-text-field>
            <v-btn
              :disabled="!fileUploaded"
              @click="sendMessage"
              @keyup.enter.native="sendMessage"
              color="primary"
            >
              <v-icon v-if="loading" class="mr-2">mdi-loading mdi-spin</v-icon>
              发送
            </v-btn>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-app>
</template>

<script>
import { defineComponent } from "vue";


export default defineComponent({
  data() {
    return {
      file: null,
      uploadStatus: null,
      messageInput: "",
      answer: "上传文档之后，如果提问没有反应，请稍等一会再提问",
      fileId: "",
      fileUploaded: true,
      loading: false,
      md: new MarkdownIt(),
    };
  },
  computed: {
    renderedMarkdown() {
      return this.md.render(this.answer);
    },
  },
  methods: {
    uploadFile() {
      if (!this.file) return;

      let formData = new FormData();
      formData.append("file", this.file);
      const url_upload = `${this.$backendUrl}/uploadDoc`;

      fetch(url_upload, {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            this.fileId = data.fileId;
            this.fileUploaded = true;
            this.uploadStatus = "文件上传完成：" + data.fileId;
          } else {
            this.uploadStatus = "文件上传失败";
          }
        });
    },

    async sendMessage() {
      this.answer = "";
      //
      if (!this.fileUploaded || this.messageInput.trim() === "") return;
      // this.loading = true;
      try {
        // if (this.messageInput.trim() === '') return;
        const url = `${this.$backendUrl}/askDoc`;

        const response = await fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: this.messageInput,
            fileIds: this.fileId,
          }),
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            console.log("我的任务完成了");
            this.loading = false;
            break;
          }
          this.answer += decoder.decode(value, { stream: true });
        }
        this.answer += decoder.decode();
        this.messageInput = "";
      } catch (error) {
        console.error("Error fetching data:", error);
        this.answer = "获取失败";
      } finally {
        // this.loading = false;
        this.messageInput = "";
      }
    },
  },
});
</script>

<style scoped>
.chat-messages {
  border: 1px solid #ccc;
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 10px;
  overflow-y: auto;
  max-height: 300px;
}

.message {
  margin-bottom: 5px;
  padding: 5px 10px;
  border-radius: 10px;
  display: inline-block;
}

.from-user {
  background-color: #c3e88d;
}

.from-bot {
  background-color: #82aaff;
}

.input-row {
  position: fixed;
  bottom: 0;
  width: calc(100% - 16px);
}

.markdown-body {
  max-height: 800px;
  overflow-y: auto;
}
</style>
