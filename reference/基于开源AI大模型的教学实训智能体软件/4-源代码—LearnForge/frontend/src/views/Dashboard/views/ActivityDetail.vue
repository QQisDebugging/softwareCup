<template>
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

                <v-md-preview :text="activityDetails.description"></v-md-preview>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>


      <!-- 右侧：学生提交列表 -->
      <v-col cols="12" md="6">
        <v-list lines="three" dense v-if="activityDetails.student_assignments.length > 0">
          <v-list-item v-for="(assignment, index) in activityDetails.student_assignments"
            :key="assignment.assignment_id" @click="showSubmissionDialog(assignment)">
            <template v-slot:prepend>
              <v-avatar color="blue">
                <span class="text-h9">{{ assignment.student_name.charAt(0) }}</span>
              </v-avatar>
            </template>

            <v-list-item-content>
              <v-list-item-title>{{ assignment.student_name }}的作业</v-list-item-title>
              <v-list-item-subtitle v-html="formattedSubmissionDate(assignment.submission_date)"></v-list-item-subtitle>
            </v-list-item-content>

            <template v-slot:append>
              <v-chip>{{ index + 1 }}</v-chip>
            </template>
          </v-list-item>
        </v-list>

        <!-- 显示空状态 -->
        <v-empty-state v-else title="暂无作业提交记录" image="https://vuetifyjs.b-cdn.net/docs/images/components/v-empty-state/astro-cat.svg"
          :actions="[]"></v-empty-state>
      </v-col>

    </v-row>

    <!-- Dialog for showing detailed submission -->
    <v-dialog v-model="dialog" max-width="800">
      <v-card>
        <v-toolbar dark color="primary">
          <v-btn icon @click="dialog = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-toolbar-title>作业详情</v-toolbar-title>
          <v-spacer></v-spacer>
        </v-toolbar>

        <v-card-text>
          <!-- <div class="markdown-body" v-html="renderedMarkdown(selectedAssignment.content)"></div> -->
          <v-md-preview :text="renderedMarkdown(selectedAssignment.content)"></v-md-preview>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import axios from '@/utils/axiosConfig';
import moment from 'moment';
// import MarkdownIt from 'markdown-it';

// import mdKatex from '@traptitech/markdown-it-katex'
// import hljs from 'highlight.js';
export default {
  props: ['activity_id'],
  data() {
    return {
      activityDetails: {
        student_assignments: []
      },
      error: '',
      dialog: false,
      selectedAssignment: null
    };
  },
  created() {
    this.fetchActivityDetails();
  },
  setup() {
    // const md = new MarkdownIt({
    //   linkify: true,
    //   highlight(code, language) {
    //     const validLang = !!(language && hljs.getLanguage(language))
    //     if (validLang) {
    //       const lang = language ?? ''
    //       return highlightBlock(hljs.highlight(lang, code, true).value, lang)
    //     }
    //     return highlightBlock(hljs.highlightAuto(code).value, '')
    //   }
    // })
    // md.use(mdKatex, { blockClass: 'katexmath-block rounded-md p-[10px]', errorColor: ' #cc0000' })

    // function highlightBlock(str, lang) {
    //   return `<pre class="pre-code-box"><div class="pre-code-header"></div><div class="pre-code"><code class="hljs code-block-body ${lang}">${str}</code></div></pre>`
    // }

    function renderedMarkdown(str) {
      try {

        const jsonObject = JSON.parse(str);


        const codeValue = jsonObject.code || '获取代码失败';
        const analyseValue = jsonObject.analyse_result || '未获取到批改结果';


        let markdownStr = `# 代码：\n\`\`\`python\n${codeValue}\n\`\`\`\n\n# AI批改：\n${analyseValue}`;


        return markdownStr;
      } catch (error) {

        return '正在加载...';
      }
    }

    function render(str) {
      try {
        return md.render(str);
      } catch (error) {

        return md.render('正在加载... ');
      }
    }




    return {
      renderedMarkdown,
      render
    }

  },
  methods: {
    formattedSubmissionDate(submissionDate) {
      return moment(submissionDate).format('YYYY-MM-DD HH:mm');
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
    showSubmissionDialog(assignment) {
      console.log(assignment);
      this.selectedAssignment = assignment;
      this.dialog = true;
    },
    isLastItem(item) {
      const lastIndex = this.activityDetails.student_assignments.length - 1;
      return item === this.activityDetails.student_assignments[lastIndex];
    }
  }
};
</script>

<style scoped>
.markdown-body {
  border: 1px solid #ccc;
  padding: 16px;
}

.details-section {
  padding: 16px;
  overflow: auto;
}

.v-list-item {
  cursor: pointer;
}

.v-list-item-avatar img {
  border-radius: 50%;
}

.v-list-item-title,

.v-list-item-subtitle {
  white-space: normal;
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
