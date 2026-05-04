<template>
  <link rel="stylesheet"
    href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/4.0.0/github-markdown.min.css">
  <v-app>
    <v-main>
      <v-container fluid>
        <v-alert v-if="error" type="error" dismissible>
          {{ error }}
        </v-alert>

        <v-row no-gutters fill-height>
          <!-- 左侧：任务详情 -->
         <v-col cols="12" md="6" class="details-section">
  <v-card outlined>
    <v-card-title class="headline">
      {{ activityDetails.activity_name }}
    </v-card-title>
    <v-card-text>
      <v-row>
        <v-col cols="12">
          <div><strong>创建者教师编号:</strong> {{ activityDetails.creator_tno }}</div>
          <v-divider class="my-2"></v-divider>
          <div><strong>创建日期:</strong> {{ formattedSubmissionDate(activityDetails.created_date) }}</div>
          <v-divider class="my-2"></v-divider>
          <div><strong>任务详情:</strong></div>
          <v-divider class="my-2"></v-divider>
          <div class="markdown-body" v-html="render(activityDetails.description)"></div>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</v-col>


          <!-- 右侧：任务提交模块 -->
          <v-col cols="12" md="6" class="submission-section">

            <v-row>
              <v-col cols="2" class="mb-4"> <!-- 添加底部间距 -->
                <v-btn @click="checkSubmissionConditions" color="primary" block>提交</v-btn>
              </v-col>
              <v-col cols="2" class="mb-4"> <!-- 添加底部间距 -->
                <v-btn @click="dialog = true" color="secondary" block>AI批改</v-btn>
              </v-col>
            </v-row>

            <codemirror v-model="code" :extensions="currentExtensions" @ready="handleReady" />

          </v-col>
        </v-row>

        <!-- AI解答全屏对话框 -->
        <v-dialog v-model="dialog" transition="dialog-bottom-transition" fullscreen @open="renderedMarkdown = '';">
          <v-card>
            <v-toolbar>
              <v-btn icon="mdi-arrow-left" @click="dialog = false"></v-btn>
              <v-toolbar-title>AI批改</v-toolbar-title>
              <v-spacer></v-spacer>
              <v-btn @click="getFigureout" icon>
                <v-icon>mdi-lightbulb-on</v-icon>
              </v-btn>
            </v-toolbar>

            <div class="markdown-body" v-html="renderedMarkdown"></div>
          </v-card>
        </v-dialog>

        <!-- 提交确认对话框 -->
        <v-dialog v-model="confirmSubmissionDialog" max-width="500px">
          <v-card>
            <v-card-title class="headline">确认提交</v-card-title>
            <v-card-text>你确定要提交当前代码吗？包括你的代码和AI批改的结果</v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="blue darken-1" text @click="confirmSubmissionDialog = false">取消</v-btn>
              <v-btn color="blue darken-1" text @click="submitAssignment">确认</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <v-dialog v-model="submissionFailedDialog" max-width="500px">
          <v-card>
            <v-card-title class="headline">oops</v-card-title>
            <v-card-text>先让AI批改一下吧~</v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="blue darken-1" text @click="submissionFailedDialog = false">确定</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import axios from '@/utils/axiosConfig';
import moment from 'moment';
import { ref, computed } from 'vue';
import MarkdownIt from 'markdown-it';
import { oneDark } from '@codemirror/theme-one-dark';
import { python } from '@codemirror/lang-python';
import mdKatex from '@traptitech/markdown-it-katex'
import hljs from 'highlight.js';
export default {
  props: ['activity_id'],
  data() {
    return {
      activityDetails: {},
      assignmentContent: '',
      code: ` ┏┓　　　┏┓
 ┏┛┻━━━┛┻┓
┃　　　　　　　┃
 ┃　　　━　　　┃
┃　┳┛　┗┳　┃
┃　　　　　　　┃
┃　　　┻　　　┃
┃　　　　　　　┃
┗━┓　　　┏━┛
┃　　　┃ 
 ┃　　　┃ 这里输入你的答案~
┃　　　┗━━━┓
┃　　　　　　　┣┓
┃　　　　　　　┏┛
┗┓┓┏━┳┓┏┛
┃┫┫　┃┫┫
┗┻┛　┗┻┛
      `,
      error: '',
      dialog: false,
      confirmSubmissionDialog: false,
      submissionFailedDialog: false,
      isStreaming: false,
      
    };
  },
  created() {
    this.fetchActivityDetails();
  },
  setup(props) {

    const currentExtensions = computed(() => {
      return [python()].concat(oneDark);
    });

    const md = new MarkdownIt({
      linkify: true,
      highlight(code, language) {
        const validLang = !!(language && hljs.getLanguage(language))
        if (validLang) {
          const lang = language ?? ''
          return highlightBlock(hljs.highlight(lang, code, true).value, lang)
        }
        return highlightBlock(hljs.highlightAuto(code).value, '')
      }
    })
    md.use(mdKatex, { blockClass: 'katexmath-block rounded-md p-[10px]', errorColor: ' #cc0000' })

    function highlightBlock(str, lang) {
      return `<pre class="pre-code-box"><div class="pre-code-header"></div><div class="pre-code"><code class="hljs code-block-body ${lang}">${str}</code></div></pre>`
    }

    const aiResponse = ref('点击右上角，开始AI批改');
    const renderedMarkdown = computed(() => md.render(aiResponse.value));
    function render(str) {
      try {
        return md.render(str);
      } catch (error) {

        return md.render('出现错误');
      }
    }

    return {
      currentExtensions,
      renderedMarkdown,
      aiResponse,
      render,
      isStreaming: ref(false)
    };
  },
  methods: {
    formattedSubmissionDate(submissionDate) {
      return moment(submissionDate).format('YYYY-MM-DD HH:mm');
    },
    checkSubmissionConditions() {
      const minCodeLength = 200000;
      const minAiResponseLength = 15;

      if ( this.aiResponse.length >= minAiResponseLength) {
        this.confirmSubmissionDialog = true;
      } else {
        this.submissionFailedDialog = true;
      }
    },
    async fetchActivityDetails() {
      this.error = '';
      try {
        const response = await axios.get(`${this.$backendUrl}/api/getActivityDetails`, {
          params: { activity_id: this.activity_id }
        });
        this.activityDetails = response.data;
        console.log(response.data);
      } catch (error) {
        if (error.response && error.response.data) {
          this.error = error.response.data.error;
        } else {
          this.error = '请求失败，请稍后再试';
        }
      }
    },
    async submitAssignment() {
        await axios.post(`${this.$backendUrl}/api/submitAssignmentAnswers`, {
          sno: localStorage.getItem('username'),
          activity_id: this.activity_id,
          content: this.code,
          analyse_result:this.aiResponse,
        })
        .then(response => {
          this.$router.push({ name: 'GetStudetActivity' }); // Redirect to activity list page after submission
        })
        .catch(error => {
          console.error('提交作业失败', error);
        });
        this.confirmSubmissionDialog = false; // Close the dialog after submission
    },
    async getFigureout() {
      const questionP = `${this.activityDetails.description}`;
      // console.log('获取解答按钮点击'); // 添加日志
      this.isStreaming = true;
      this.aiResponse = '';

      const url = `${this.$backendUrl}/api/spark/ques_analyse`;

      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ques: questionP, mycode: this.code })
        });

        if (!response.body) {
          throw new Error('Failed to get readable stream.');
        }

        const reader = response.body.getReader();
        while (this.isStreaming) {
          const { done, value } = await reader.read();
          if (done) {
            break;
          }
          this.aiResponse += new TextDecoder().decode(value);
          console.log(this.aiResponse)
        }
        console.log('AI响应:', this.aiResponse); // 添加日志
      } catch (error) {
        console.error("Failed to send query: ", error);
        this.aiResponse = "响应失败.";
      } finally {
        this.isStreaming = false;
      }
    }
  }
};
</script>

<script setup>

</script>

<style scoped>
.v-row {
  flex: 1;
  display: flex;
}

.details-section,
.submission-section {
  /* flex-direction: column; */
  padding: 16px;
  overflow: auto;
}

/* .details-section {
  background-color: #f5f5f5;
} */

.submission-section {
  background-color: #ffffff;
}



.v-btn {
  align-self: flex-end;
}

.markdown-body {
  border: 1px solid #ccc;
  padding: 16px;
}

.details-section {
  padding: 16px;
}

.headline {
  font-weight: bold;
  font-size: 1.25rem;
}
.my-2 {
  margin-top: 8px;
  margin-bottom: 8px;
}
.mt-2 {
  margin-top: 8px;
}
</style>
