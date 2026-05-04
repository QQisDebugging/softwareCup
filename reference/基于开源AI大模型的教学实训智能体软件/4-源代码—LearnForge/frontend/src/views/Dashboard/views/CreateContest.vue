<template>
  <v-app>
    <v-container>
      <v-form @submit.prevent="submitForm">
        <v-text-field
          label="关于什么知识点的知识"
          v-model="info"
          required
        ></v-text-field>

        <v-text-field
          label="用户要求（可不填）"
          v-model="query"
          required
        ></v-text-field>

        <v-select
          label="题目类型"
          v-model="type"
          :items="types"
          required
        ></v-select>

        <v-slider
          label="题目数量"
          v-model="count"
          :min="1"
          :max="15"
           step="1"
          ticks
          tick-size="2"
          thumb-label="always"
          required
       
        ></v-slider>
        <v-btn type="submit" color="primary">生成</v-btn>
        <v-btn v-if="response" color="success" @click="publish">发布</v-btn>
      </v-form>

      <v-dialog v-model="loading" hide-overlay persistent width="300">
        <v-card>
          <v-card-text>生成中，请坐和放宽。。。</v-card-text>
          <v-progress-linear indeterminate color="primary"></v-progress-linear>
        </v-card>
      </v-dialog>

      <v-divider></v-divider>

      <v-card v-if="response">
        <v-card-title>题目如下：</v-card-title>
        <component :is="currentComponent" :questionsJson="questionsJson" />
        
      </v-card>

      <v-dialog v-model="publishDialog" fullscreen hide-overlay persistent>
        <v-card>
          <v-toolbar dark color="primary">
            <v-toolbar-title>发布题目</v-toolbar-title>
            <v-spacer></v-spacer>
            <v-btn icon @click="publishDialog = false">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-toolbar>
          <v-card-text>
            <v-form @submit.prevent="submitContest">
              <v-text-field
                label="作业名称"
                v-model="contestName"
                required
              ></v-text-field>
              <v-select v-model="selectedClasses" :items="classes" item-title="ClassName"
                                item-value="ClassID" label="选择班级" multiple chips dense></v-select>
              <v-btn type="submit" color="primary">提交</v-btn>
            </v-form>
            <component :is="currentComponent" :questionsJson="questionsJson" />
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-container>
  </v-app>
</template>

<script>
import axios from '@/utils/axiosConfig';
import ChoiceQuestionListTeacher from '@/components/ChoiceQuestionListTeacher.vue';
import JudgeQuestionListTeacher from '@/components/JudgeQuestionListTeacher.vue';
import BriefQuestionListTeacher from '@/components/BriefQuestionListTeacher.vue';

export default {
  components: {
    ChoiceQuestionListTeacher,
    JudgeQuestionListTeacher,
    BriefQuestionListTeacher
  },
  data() {
    return {
      selectedClasses: [],
      info: '',
      query: '',
      type: '',
      count: 5,
      types: ['选择题', '判断题', '问答题'],
      loading: false,
      response: null,
      questionsJson: null,
      publishDialog: false,
      contestName: '',
  
      classId: ''
    };
  },
  mounted() {
        this.getClasses(); // 获取班级列表
    },
  computed: {
    currentComponent() {
      switch (this.type) {
        case '选择题':
          return 'ChoiceQuestionListTeacher';
        case '判断题':
          return 'JudgeQuestionListTeacher';
        case '问答题':
          return 'BriefQuestionListTeacher';
        default:
          return null;
      }
    }
  },
  methods: {
    getClasses() {
            axios.get(`${this.$backendUrl}/api/getClasses`)
                .then(response => {
                    this.classes = response.data; // 设置班级列表
                    console.log(response.data);
                })
                .catch(error => {
                    console.error('获取班级列表失败', error);
                });
        },
    async submitForm() {
      const params = {
        info: this.info,
        query: this.query,
        type: this.type,
        count: this.count
      };

      this.loading = true;
      this.response = null;
      this.questionsJson = null;

      try {
        const response = await axios.post(`${this.$backendUrl}/api/spark/generateContest`, params, {
          responseType: 'text'
        });

        this.response = response.data;
        try {
          this.questionsJson = JSON.stringify(JSON.parse(this.response));  // 确保 questionsJson 是一个 JSON 字符串
        } catch (parseError) {
          console.error('JSON 解析错误:', parseError);
          this.response = '返回的数据不是有效的 JSON';
        }
      } catch (error) {
        console.error(error);
        this.response = '请求失败';
      } finally {
        this.loading = false;
      }
    },
    publish() {
      this.publishDialog = true;
    },
    closeDialog() {
      this.publishDialog = false;
    },

    async submitContest() {
      const params = {
        creatorName: localStorage.getItem("username","2000001"),
        contestName: this.contestName,
        questionJson: this.questionsJson,
        questionType: this.type,
        publishDate: new Date().toISOString(),
        selectedClasses: this.selectedClasses
      };

      try {
        const response = await axios.post(`${this.$backendUrl}/api/createContest`, params);
        console.log('Contest submitted:', response.data);
        this.closeDialog();
      } catch (error) {
        console.error('提交失败:', error);
      }
    }

  }
};
</script>

<style>
/* 可根据需要添加样式 */
</style>
