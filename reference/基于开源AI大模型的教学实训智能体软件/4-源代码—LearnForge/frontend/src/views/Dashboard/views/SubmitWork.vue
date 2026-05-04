<template>
    <v-container>
      <v-stepper v-model="step">
        <!-- Stepper Headers -->
        <v-stepper-header>
          <template v-for="(task, index) in tasks" :key="index">
            <v-stepper-item
              :complete="e1 > n"
             
              :value="task.知识点"
              
              editable
            ></v-stepper-item>
            <v-divider v-if="index !== tasks.length - 1"></v-divider>
          </template>
        </v-stepper-header>
  
        <!-- Stepper Items -->
        <v-stepper-items>
          <template v-for="(task, index) in tasks" :key="index">
            <v-stepper-content :step="index + 1">
              <v-card class="mb-5" flat>
                <v-card-title>任务 {{ index + 1 }}</v-card-title>
                <v-card-text>
                  <div><strong>知识点:</strong> {{ task.知识点 }}</div>
                  <div><strong>题目:</strong> {{ task.题目 }}</div>
                  <v-textarea 
                    v-model="answers[index]" 
                    label="输入您的答案" 
                    rows="5" 
                  ></v-textarea>
                </v-card-text>
                <v-card-actions>
                  <v-btn 
                    text 
                    @click="prevStep" 
                    v-if="index > 0"
                  >
                    上一步
                  </v-btn>
                  <v-btn 
                    color="primary" 
                    @click="nextStep" 
                    v-if="index < tasks.length - 1"
                  >
                    下一步
                  </v-btn>
                  <v-btn 
                    color="primary" 
                    @click="submitAssignment" 
                    v-if="index === tasks.length - 1"
                  >
                    提交
                  </v-btn>
                  <v-btn 
                    color="secondary" 
                    @click="saveProgress"
                  >
                    暂存
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-stepper-content>
          </template>
        </v-stepper-items>
      </v-stepper>
  
      <!-- Snackbar -->
      <v-snackbar v-model="snackbar" :timeout="timeout">
        {{ snackbarMessage }}
        <!-- <v-btn color="pink" text @click="snackbar = false">关闭</v-btn> -->
      </v-snackbar>
    </v-container>
  </template>
  
  <script>
  import axios from '@/utils/axiosConfig';
  import moment from 'moment';
  
  export default {
    data() {
      return {
        step: 1,
        assignmentDetails: {},
        tasks: [],
        answers: [],
        assignment_id: this.$route.params.assignment_id,
        sno: localStorage.getItem('username'),
        snackbar: false,
        snackbarMessage: '',
        timeout: 3000
      };
    },
    mounted() {
      this.fetchAssignmentDetails();
    },
    methods: {
      formattedDate(date) {
        return moment(date).format('YYYY-MM-DD HH:mm');
      },
      async fetchAssignmentDetails() {
        try {
          const response = await axios.get(`${this.$backendUrl}/api/getAssignmentDetails`, {
            params: { assignment_id: this.assignment_id }
          });
          this.assignmentDetails = response.data;
          this.tasks = JSON.parse(this.assignmentDetails.tasks_json);
          this.loadProgress();
        } catch (error) {
          console.error('获取作业详情失败', error);
          this.$alert(`错误: ${error.response.data.error}`);
        }
      },
      nextStep() {
        if (this.step < this.tasks.length) {
          this.step++;
        }
      },
      prevStep() {
        if (this.step > 1) {
          this.step--;
        }
      },
      async submitAssignment() {
        try {
          const response = await axios.post(`${this.$backendUrl}/api/submitWorkAnswers`, {
            assignment_id: this.assignment_id,
            sno: this.sno,
            answers: this.answers,
          });
          this.snackbarMessage = '提交成功';
          this.snackbar = true;
        //   this.$router.push({ name: 'StudentAssignments' });
        } catch (error) {
            this.snackbarMessage = '提交失败';
            this.snackbar = true;
        }
      },
      saveProgress() {
        localStorage.setItem(`assignment_${this.assignment_id}_answers`, JSON.stringify(this.answers));
        this.snackbarMessage = '进度已暂存';
        this.snackbar = true;
      },
      loadProgress() {
        const savedAnswers = localStorage.getItem(`assignment_${this.assignment_id}_answers`);
        if (savedAnswers) {
          this.answers = JSON.parse(savedAnswers);
        } else {
          this.answers = this.tasks.map(() => ''); // 初始化每个任务的答案为空
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .v-container {
    max-width: 1000px;
    margin: auto;
  }
  
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
  