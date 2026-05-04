<template>
    <v-container>
      <v-alert v-if="error" type="error" dismissible>
        {{ error }}
      </v-alert>
  
      <v-card class="mb-4">
        <v-card-title>
          <v-icon left>mdi-information</v-icon>
          {{ assignmentDetails.assignment_name }}
        </v-card-title>
        <v-card-text>
          <div><strong>创建者编号:</strong> {{ assignmentDetails.creator_tno }}</div>
          <div><strong>创建者姓名:</strong> {{ assignmentDetails.creator_name }}</div>
          <div><strong>发布日期:</strong> {{ formattedDate(assignmentDetails.publish_date) }}</div>
        </v-card-text>
      </v-card>
  
      <v-divider class="my-4"></v-divider>
  
      <v-card class="mb-4">
        <v-card-title>
          <v-icon left>mdi-file-document</v-icon>
          任务列表
        </v-card-title>
        <v-card-text>
          <v-expansion-panels v-if="tasks.length" v-model="panel" multiple>
            <v-expansion-panel v-for="(task, index) in tasks" :key="index">
              <v-expansion-panel-title>{{ index + 1 }}. {{ task.知识点 }}</v-expansion-panel-title>
              <v-expansion-panel-text>{{ task.题目 }}</v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-card-text>
      </v-card>
  
      <v-divider class="my-4"></v-divider>
  
      <v-card class="mb-3">
        <v-card-title>
          <v-icon left>mdi-trophy-variant</v-icon>
          学生提交情况
        </v-card-title>
        <v-card-text>
          <v-table>
            <thead>
              <tr>
                <th class="text-left">排行</th>
                <th class="text-left">学号</th>
                <th class="text-left">姓名</th>
                <th class="text-left">专业</th>
                <th class="text-left">提交时间</th>
                <th class="text-left">分数</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(student, index) in assignmentDetails.student_submissions" :key="index">
                <td><v-chip color="primary" variant="elevated">{{ index + 1 }}</v-chip></td>
                <td>{{ student.sno }}</td>
                <td>{{ student.name }}</td>
                <td>{{ student.major }}</td>
                <td>{{ formattedDateWithoutYear(student.submission_date) }}</td>
                <td>{{ student.score }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-card-text>
      </v-card>
    </v-container>
  </template>
  
  <script>
  import axios from '@/utils/axiosConfig';
  import moment from 'moment';
  
  export default {
    props: ['assignment_id'],
    data() {
      return {
        assignmentDetails: {},
        tasks: [],
        panel: [],
        error: ''
      };
    },
    created() {
      this.fetchAssignmentDetails();
    },
    methods: {
      formattedDateWithoutYear(date) {
        return moment(date).format('MM-DD HH:mm');
      },
      formattedDate(date) {
        return moment(date).format('YYYY-MM-DD HH:mm');
      },
      async fetchAssignmentDetails() {
        this.error = '';
        try {
          const response = await axios.get(`${this.$backendUrl}/api/getAssignmentDetails`, {
            params: { assignment_id: this.assignment_id }
          });
          this.assignmentDetails = response.data;
          this.tasks = JSON.parse(this.assignmentDetails.tasks_json);
        } catch (error) {
          if (error.response && error.response.data) {
            this.error = error.response.data.error;
          } else {
            this.error = '请求失败，请稍后再试';
          }
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .v-container {
    max-width: 800px;
    margin: auto;
  }
  
  /* Card styling */
  .v-card {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
  }
  
  .v-card-title {
    border-bottom: 1px solid #e0e0e0;
    padding: 10px;
  }
  
  .v-card-text > div {
    margin-bottom: 5px;
    padding: 5px 10px;
  }
  </style>
  